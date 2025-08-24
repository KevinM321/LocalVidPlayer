const api_path = "/player/"
const vid_path = "/vids/";

var current = 0;
var list_current = 0;
var list_increment = 8;
var list_bool = false;

var terminal = false;
var term_max_lines = 4;

var muted = false;
var locked = false;
var paused = false;
var display_scale = 100;
var display_rotation = 0;
var display_reflections = [1, 1];

var playback_speed = 1.0;
var min_speed = 0.25;
var max_speed = 3;
var zoom_out_count = 0;

const gaps = [1, 2, 3, 5, 10, 15, 20, 30, 50];
var current_gap = 2;
var change_gap = true;
var listing = false;

const temp = document.getElementById("term_line_temp");
function termLog(command, results) {
    var term_output = document.getElementById('term_output');
    if (term_output.children.length == term_max_lines) {
        var lc = term_output.lastElementChild;
        term_output.removeChild(lc);
    }

    const clone = temp.content.cloneNode(true);
    clone.querySelector('.prompt').textContent = `> ${new Date().toLocaleTimeString()}`;
    clone.querySelector('.command').textContent = `${command}`;
    clone.querySelector('.result').textContent = `${results.response}`;

    const line = document.createElement("div");
    line.setAttribute('class', 'term_line');
    line.appendChild(clone);
    if (!results.status) {
        line.style.backgroundColor = "rgba(255, 0, 0, .6)";    
    }

    term_output.prepend(line);
}

function transformVid() {
    var display = document.getElementById('main_display');
    var x = display_reflections[0];
    var y = display_reflections[1];
    display.style.transform = `rotate(${display_rotation}deg) scaleX(${x}) scaleY(${y})`;
}

function sanitize(input) {
    return input
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

function scaleVideo() {
    const wrapper = document.getElementById('wrapper');
    const display = document.getElementById('main_display');
    const prevWidth = display.offsetWidth;
    const prevHeight = display.offsetHeight;

    const centerX = wrapper.scrollLeft + wrapper.clientWidth / 2;
    const centerY = wrapper.scrollTop + wrapper.clientHeight / 2;

    const offsetX = (centerX - display.offsetLeft) / prevWidth;
    const offsetY = (centerY - display.offsetTop) / prevHeight;

    display.style.height = `${display_scale}vh`;

    requestAnimationFrame(() => {
        const newWidth = display.offsetWidth;
        const newHeight = display.offsetHeight;

        wrapper.scrollLeft = display.offsetLeft + newWidth * offsetX - wrapper.clientWidth / 2;
        wrapper.scrollTop = display.offsetTop + newHeight * offsetY - wrapper.clientHeight / 2;
    });
    wrapper.focus();
}

function zoomOut() {
    if (display_scale > 10) {
        display_scale -= 10;
        scaleVideo();

        if (display_scale < 100) {
            zoom_out_count++;
            document.getElementById('topblock').style.height = `${zoom_out_count * 5}vh`;    
        }
    }
}

function zoomIn() {
    if (display_scale < 300) {
        display_scale += 10;
        scaleVideo();

        if (display_scale < 110) {
            zoom_out_count--;
            document.getElementById('topblock').style.height = `${zoom_out_count * 5}vh`;    
        }
    }
}

function createVideo(metadata, muted){
    var source = document.createElement('source');
    source.setAttribute('src', vid_path + metadata.title + `#t=${metadata.start_t}`);
    source.setAttribute('type', 'video/mp4');
	source.setAttribute('id', "display_source")

    var display = document.createElement('video');
    display.setAttribute('id', 'main_display');
	display.setAttribute('class', 'mainvideo');
    display.setAttribute('tabindex', '-1');
	display.setAttribute('autoplay', '');
    display.setAttribute('name', 'media');
	if (!muted) {
		display.setAttribute('onloadstart', `this.volume=${metadata.volume/100}`);
	} else {
		display.setAttribute('onloadStart', 'this.volume=0');
	}

    display.appendChild(source);

    return display;
}

function setVideo(metadata, remove, muted){
    var body = document.getElementById('display_body');
	playback_speed = 1.0;

    if (remove){
        var display = document.getElementById('main_display');
		if (document.pictureInPictureElement){
			document.exitPictureInPicture();
		}
        body.removeChild(display);
    }
    var display = createVideo(metadata, muted);
    body.appendChild(display);

    display_reflections[0] = metadata.reflection_x;
    display_reflections[1] = metadata.reflection_y;
    display_rotation = metadata.rotation;

    display_scale = 100;
    zoom_out_count = 0;
    document.getElementById('topblock').style.height = `${zoom_out_count * 5}vh`;    
    scaleVideo();
    const intervalId = setInterval(() => {
        if (display_scale < metadata.scale) zoomIn();
        if (display_scale > metadata.scale) zoomOut();

        if (display_scale == metadata.scale) {
            clearInterval(intervalId);
        }
    }, 20);    
    transformVid();
}

async function processVideo(metadata, remove, muted) {
    var _ = await getHighlights(metadata.id);
    curr_h = 0;
    if (highlights.length != 0) metadata.start_t = highlights[0];
    setVideo(metadata, remove, muted);
}

async function getHighlights(vid) {
    var res = await fetch(`${api_path}get_highlight?vid_id=${vid}`);
    highlights = await res.json();
    console.log(highlights);
}

function gotoVideo(num, metadatas){
	current = num
	processVideo(metadatas[current], true, muted);
}

function createList(count, metadatas){
	var l = document.getElementById('list');
	var i = 0;
	var length = list_increment;
	l.textContent = '';

	while (i + list_current < count){
		if (length == 0) break;
		let vi = i + list_current;
		var source = document.createElement('source');

        var metadata = metadatas[vi];
		source.setAttribute('src', vid_path + metadata.title + `#t=${metadata.start_t}`);
    	source.setAttribute('type', 'video/mp4');

		var vid = document.createElement('video');
		vid.setAttribute('class', 'thumbnail');
        vid.addEventListener('click', () => gotoVideo(vi, metadatas));
		vid.appendChild(source);
		l.appendChild(vid);
		
		i += 1;
		length -= 1;
	}
}

function setupTerminal() {
    var con_body = document.getElementById("term_body");
    con_body.style.display = 'none';
}

function displayMessage(message, duration){
    var d = document.createElement('section');
    var char = document.createElement('P');
    var body = document.getElementById('display_body');
    
    d.setAttribute('id', 'display');
    char.setAttribute('id', 'char');
    char.textContent = message;
    d.appendChild(char);
    body.appendChild(d);

    setTimeout(()=>{
        d.removeChild(char);
        body.removeChild(d);
    }, 1000 * duration);
}


async function modifyMetadata(action, id, val) {
    let res = await fetch(api_path + action, {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({'id': id,
                            'value': val
        })
    });
    res = await res.json();
    return res;
}


var metadatas;
var vid_count;
var highlights;
var curr_h;

async function setupPlayer() {
    // var response = await fetch(api_path + 'config/frontend');
    // var body = await response.json();

    var response = await fetch(api_path + 'reload');
    var body = await response.json();
    console.log(body.response);
    if (!body.status) return;

    response = await fetch(api_path + 'metadatas');
    metadatas = await response.json();
    vid_count = metadatas.length;
}

async function checkNoParam(params) {
    let action = params[0].toLowerCase();
    let id = metadatas[current].id;

    if (action == 'rot') {
        var res = await modifyMetadata('rotation', id, display_rotation);
        termLog(action, res);
        if (res.status) metadatas[current].rotation = display_rotation;
    }
    else if (action == 'refl') {
        var res = await modifyMetadata('reflection_x', id, display_reflections[0]);
        if (res.status) {
            metadatas[current].reflection_x = display_reflections[0];
            res = await modifyMetadata('reflection_y', id, display_reflections[1]);
        }
        termLog(action, res);
        if (res.status) metadatas[current].reflection_y = display_reflections[1];
    }
    else if (action == 'scale') {
        var s = display_scale;
        var z = zoom_out_count;

        var res = await modifyMetadata('scale', id, s);
        if (res.status) res = await modifyMetadata('zoom', id, z);
        termLog(action, res);

        if (res.status) {
            metadatas[current].scale = s;
            metadatas[current].zoom = z;
        }
    }
    else if (action == 'highlights') {
        termLog(action, {'status': 1, 'response': highlights});
        console.log(highlights);
    }
    else if (action == 'remove' || action == 'rm') {
        var res = await modifyMetadata('remove', id, metadatas[current].title);
        termLog(action, res);
    }
    else if (action == 'name') {
        termLog(action, {'status': 1, 'response': metadatas[current].title});
    }
    else if (action == 'clear') {
        document.getElementById('term_output').textContent = "";
    }
    else {
        termLog(action, {'status': 0, 'response': 'Invalid Command'});
    }
}

async function checkOneParam(params) {
    let action = params[0].toLowerCase();
    let val = params[1].toLowerCase();
    let id = metadatas[current].id;

    if (action == 'vol') {
        var res = await modifyMetadata('volume', id, val);
        termLog(action, res);
        if (res.status) metadatas[current].volume = parseInt(val, 10);
    }
    else if (action == 'hl') {
        var res = await modifyMetadata('add_highlight', id, val);
        termLog(action, res);
    }
    else if (action == 'rmhl') {
        var res = await fetch(api_path + `remove_highlight?vid_id=${id}&timestamp=${val}`);
        var body = await res.json();
        termLog(action, body);
    }
    else if (action == 'goto') {
        var num = Number(val);
        var valid = Number.isInteger(num);
        if (valid && num >= 1 && num <= vid_count) {
            current = num - 1;
            setVideo(metadatas[current], true, muted)
            termLog(action, {'status': 1, 'response': 'Command Successful'});
        } else {
            termLog(action, {'status': 0, 'response': 'Invalid Video Number'});
            console.log("Invalid Number");
        }
    }
    else {
        termLog(action, {'status': 0, 'response': 'Invalid Command'});
    }
}

async function VidPlayer(){
    var _ = await setupPlayer();

    createList(vid_count, metadatas);
    document.getElementById('list').style.display = 'none';
    
    if (!vid_count) return;
    _ = await processVideo(metadatas[current], false, muted);
    var wrapper = document.getElementById('wrapper');

    wrapper.addEventListener("keydown", async (e) => {
        if (e.code == 'Space') e.preventDefault();
    });
    wrapper.focus();

    document.getElementById("term_input").addEventListener("keydown", async (e) => {
        if (e.key === "Enter") {
            const cmd = sanitize(e.target.value.trim());
            e.target.value = '';

            if (cmd.length == 0) return;
            let params = cmd.split(" ");
            if (params.length <= 1) {
                checkNoParam(params);
            } else {
                checkOneParam(params);
            }
        }
    });

    document.addEventListener('keyup', (event) => {
        event.preventDefault();
        var name = event.key;
        var code = event.code;
        var display = document.getElementById('main_display');

        if (code == "Backquote") {
            terminal = !terminal;
            var term_body = document.getElementById('term_body');
            var term_input = document.getElementById('term_input');
            if (terminal) {
                term_input.value = '';
                term_body.style.display = 'initial';
                term_input.focus();
            }
            else {
                term_body.style.display = 'none';
            }
        }

        if (!terminal) {
            if (name == '0') {
                var res = fetch(api_path + `add_highlight?vid_id=${metadatas[current].id}&timestamp=${display.currentTime}`);
            }
            if (name == 'g') {
                var hlen = highlights.length;
                if (!hlen) return;
                curr_h = (curr_h + hlen - 1) % hlen;
                display.currentTime = highlights[curr_h];
            }
            if (name == 'h') {
                var hlen = highlights.length;
                if (!hlen) return;
                curr_h = (curr_h + 1) % hlen;
                display.currentTime = highlights[curr_h];
            }
            if (name == "v") {
                displayMessage(`${display.volume * 100}\n${parseInt(display.currentTime, 10)}`, 0.6);
            }
            if (name == "e"){
                if (current != vid_count - 1 && !locked){
                    current += 1;
                    processVideo(metadatas[current], true, muted);
                } else if (!locked){
                    current = 0;
                    processVideo(metadatas[current], true, muted);
                }
            }

            if (name == "q"){
                if (current != 0 && !locked){
                    current -= 1;
                    processVideo(metadatas[current], true, muted);
                } else if (!locked){
                    current = vid_count - 1;
                    processVideo(metadatas[current], true, muted);
                }
            }
            if (name == "l"){
                var l = document.getElementById('list');
                listing = !listing;
                if (listing){
                    l.style.display = 'initial';
                } else{
                    l.style.display = 'none';
                }
            }
            if (name == "1"){
                display.currentTime = 0;
            }
            if (name == "2"){
                display.currentTime = display.duration * 0.225;
            }
            if (name == "3"){
                display.currentTime = display.duration * 0.5;
            }
            if (name == "4"){
                display.currentTime = display.duration * 0.75;
            }
            if (name == "5"){
                display.currentTime = display.duration * 0.925;
            }
            if (name == "p"){
                if (document.pictureInPictureElement) {
                    document.exitPictureInPicture();
                } else if (document.pictureInPictureEnabled) {
                    display.requestPictureInPicture();
                }
            }
            if (code == "ControlRight"){
                locked = !locked;
            }
            if (code == "Space"){
                paused = !paused;
                paused ? display.play() : display.pause();
            }
            if (name == "m") {
                if (muted) {
                    var volume = metadatas[current].volume / 100;
                    display.volume = volume;
                } else {
                    display.volume = 0;
                }
                muted = !muted;
            }
            if (name == "u"){
                if (display.hasAttribute("controls")) {
                    display.removeAttribute("controls");
                } else {
                    display.setAttribute("controls","controls");
                }
            }
            if (name == "x"){
                display.requestFullscreen()
            }
            if (name == "t"){
                const current_minutes = Math.floor(display.currentTime / 60);
                const current_seconds = Math.floor(display.currentTime - current_minutes * 60);
                const minutes = Math.floor(display.duration / 60);
                const seconds = Math.floor(display.duration - minutes * 60);
                displayMessage(current_minutes+":"+current_seconds + "\n" + minutes+":"+seconds, 0.6);
            }
            if (name == "i"){
                displayMessage((current+1) + "/" + (vid_count), 0.6);
            }
            if (name == "r") {
                display_rotation = (display_rotation + 90) % 360;
                transformVid();
            }
            if (name == "f"){
                display_reflections[(display_rotation / 90) % 2] *= -1;
                transformVid();
            }
            if (name == "b"){
                if (playback_speed - 0.25 <= min_speed) playback_speed = min_speed;
                else playback_speed -= 0.25;
                display.playbackRate = playback_speed;
                displayMessage(playback_speed, 0.6);
            }
            if (name == "n") {
                if (playback_speed + 0.25 >= max_speed) playback_speed = max_speed;
                else playback_speed += 0.25;
                display.playbackRate = playback_speed;
                displayMessage(playback_speed, 0.6);
            }
            if (name == "s"){
                if (change_gap){
                    if (current_gap - 1 >= 0){
                        current_gap -= 1;
                    }
                    displayMessage(gaps[current_gap], 0.6);
                } else{
                    if (display.volume - 0.05 < 0){
                        display.volume = 0;
                    } else{
                        display.volume -= 0.05;
                    }
                    displayMessage(Math.round(display.volume * 100), 0.6);
                }
            }
            if (name == "w"){
                if (change_gap){
                    if (current_gap + 1 <= gaps.length - 1){
                        current_gap += 1;
                    }
                    displayMessage(gaps[current_gap], 0.6);
                } else{
                    if (display.volume + 0.05 > 1){
                        display.volume = 1;
                    } else{
                        display.volume += 0.05;
                    }
                    displayMessage(Math.round(display.volume * 100), 0.6);
                }
            }
            if (name == "c"){
                change_gap = !change_gap;
                if (change_gap){
                    displayMessage("Time", 0.4);
                } else{
                    displayMessage("Volume", 0.4);
                }
            }
            if (code == "Comma"){
                if (listing){
                    if (list_current - list_increment >= 0) {
                        list_current -= list_increment;
                    } else {
                        list_current = Math.floor(vid_count / list_increment) * list_increment;
                    }
                    createList(vid_count, metadatas);
                }
            }
            if (code == "Period"){
                if (listing){
                    if (list_current + list_increment < vid_count){
                        list_current += list_increment;
                    } else {
                        list_current = 0;
                    }
                    createList(vid_count, metadatas);
                }
            }
            if (code == "Slash") {
                if (listing){
                    list_current = (list_bool) ? 0 : Math.floor(vid_count / list_increment) * list_increment;
                    createList(vid_count, metadatas);
                    list_bool = !list_bool;
                }
            }
        }
    }, false);

    document.addEventListener('mouseup', (event) => {
        var name = event.button;
        var display = document.getElementById("main_display");

        if (name == 4){
            if (current != vid_count - 1 && !locked){
                current += 1;
                processVideo(metadatas[current], true, muted);
            } else if (!locked){
                current = 0;
                processVideo(metadatas[current], true, muted);
            }
        }
        if (name == 3){
            if (current != 0 && !locked){
                current -= 1;
                processVideo(metadatas[current], true, muted);
            } else if (!locked){
                current = vid_count - 1;
                processVideo(metadatas[current], true, muted);
            }
        }
        if (name == 0){
            paused = !paused;
            paused ? display.play() : display.pause();
        }
        if (name == 2){
            const current_minutes = Math.floor(display.currentTime / 60);
            const current_seconds = Math.floor(display.currentTime - current_minutes * 60);
            const minutes = Math.floor(display.duration / 60);
            const seconds = Math.floor(display.duration - minutes * 60);
            displayMessage(current_minutes+":"+current_seconds + "\n" + minutes+":"+seconds, 0.6);
        }
    }, false);
    
    document.addEventListener('keypress', (event) => {
        var name = event.key;
        var code = event.code;
        var display = document.getElementById("main_display");

        if (!terminal) {
            if (name == "a"){
                var time = display.currentTime;
                if (time - gaps[current_gap] < 0){
                    display.currentTime = 0;
                } else{
                    display.currentTime = time - gaps[current_gap];
                }
            }
            if (name == "d"){
                var time = display.currentTime;
                var duration = display.duration;
                if (time + gaps[current_gap] > duration){
                    display.currentTime = duration;
                } else{
                    display.currentTime = time + gaps[current_gap];
                }
            }
            if (code == "BracketLeft"){
                zoomOut();
            }
            if (code == "BracketRight"){
                zoomIn();
            }
        }
    }, false);

    document.addEventListener("wheel", (event) => {
        var display = document.getElementById("main_display");

        if (!listing){
            if (event.deltaY < 0){
                if (display.volume + 0.05 > 1){
                    display.volume = 1;
                } else{
                    display.volume += 0.05;
                }
                displayMessage(Math.round(display.volume * 100), 0.6);
            } else{
                if (display.volume - 0.05 < 0){
                    display.volume = 0;
                } else{
                    display.volume -= 0.05;
                }
                displayMessage(Math.round(display.volume * 100), 0.6);
            }
        }
    }, false);
}

setupTerminal();
VidPlayer();
