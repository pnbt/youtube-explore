/**
 * Created by Guillaume on 8/13/16.
 */

var MIN_NUMBER_OF_LIKES = 1;

// Minimum size of the nodes so we can see them.
var NODE_MIN_SIZE = 1;
var videos = {};
var video_list = [];
var node, link;
var current_video_id = '';

$( document ).ready(function() {
    setTimeout(load_explaination_modals, 2000);
});

/**
 * Converts integer to a hexidecimal code, prepad's single
 * digit hex codes with 0 to always return a two digit code.
 *
 * @param {Integer} i Integer to convert
 * @returns {String} The hexidecimal code
 */
function intToHex(i) {
    var hex = parseInt(i).toString(16);
    return (hex.length < 2) ? "0" + hex : hex;
}

/**
 * Return hex color from scalar *value*.
 *
 * @param {float} value Scalar value between 0 and 1
 * @return {String} color
 */
function makeColor(value) {
    // value must be between [0, 510]
    value = Math.min(Math.max(0, value), 1) * 255;

    var redValue  = 255 - value;
    var greenValue = value;
    if (value < 255) {
        redValue = 255;
        redValue = 256 - (value * value / 255);
        redValue = Math.round(redValue);
        greenValue = Math.sqrt(value) * 16;
        greenValue = Math.round(greenValue);
    } else {
        greenValue = 255;
        value = value - 255;
        redValue = 256 - (value * value / 255);
        redValue = Math.round(redValue);
    }

    return "#" + intToHex(redValue) + intToHex(greenValue) + "00";
}

/* Initialize tooltip */
tip = d3.tip().attr('class', 'd3-tip').html(function(d) { return d.title; });

var svg = d3.select("svg").call(tip).call(d3.zoom().on("zoom", zoomed)),
    svg2 = svg.append("g"),
    width = window.innerWidth,
    height = window.innerHeight;

document.getElementById('svg').setAttribute('height', height + 'px');
document.getElementById('svg').setAttribute('width', width + 'px');

var color = d3.scaleOrdinal(d3.schemeCategory20);

var simulation = d3.forceSimulation()
    .force("link", d3.forceLink().id(function(d) { return d.id; }))
    .force("charge", d3.forceManyBody())
    .force("center", d3.forceCenter(width / 2, height / 2));

function get_size(d) {
    return parseInt(1000 * Math.sqrt(d.size)) + NODE_MIN_SIZE;
}

function get_color(d) {
    if (d.popularity === -1) return "grey";
    return makeColor(d.popularity * d.popularity * d.popularity)
}

function make_tooltip(d) {
    var tooltip = d.title + ' ';

    if (d.views > -1) {
        tooltip += d.views + ' views    ';
    }
    if (d.likes > -1 && d.dislikes) {
        tooltip += Math.floor(100 * d.likes / (d.likes + d.dislikes)) + ' % likes'
    }
    return tooltip
}

function display_graph(graph) {
    link = svg2.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(graph.links)
        .enter().append("line")
        .attr("stroke-width", 2)
//      .attr("marker-end", "url(#end)")
//      .style("opacity", function(o) {
//        return videos[o.source.id].selected ? 1 : 0.2;
//      });

    node = svg2.append("g")
        .attr("class", "nodes")
        .selectAll("circle")
        .data(graph.nodes).
        enter().append("circle")
        .attr("r", get_size)
        .style("fill", get_color)
        .on('click', update_video_iframe)
        .call(d3.helper.tooltip()
            .style({color: 'blue'})
            .text(function(d){ return 'value: '+ d.title;})
    )
        .call(d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended))
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide)

    //      .on('mouseover', function(d) {
//        link.style('stroke-width', function(l) {
//            if (d.id === l.target.id) {
//                return '5';
//            } else {
//                return '1';
//            }
//        })});
//  marker = svg.append("svg:defs").selectAll("marker")
//        .data(["end"])      // Different link/path types can be defined here
//        .enter().append("svg:marker")    // This section adds in the arrows
//        .attr("id", String)
//        .attr("viewBox", "0 -5 10 10")
//        .attr("refX", 15)
//        .attr("refY", -1.5)
//        .attr("markerWidth", 6)
//        .attr("markerHeight", 6)
//        .attr("orient", "auto")
//        .append("svg:path")
//        .attr("d", "M0,-3L10,0L0,3")
//        .style("stroke-width", 20)
//        .style("fill", "#999")
//        .style("fill-opacity", 0.6)

//  node.append("svg:title")
//      .text(make_tooltip)

    simulation
        .nodes(graph.nodes)
        .on("tick", ticked);

    simulation.force("link")
        .links(graph.links);
}

function ticked() {
    link
        .attr("x1", function(d) { return d.source.x; })
        .attr("y1", function(d) { return d.source.y; })
        .attr("x2", function(d) { return d.target.x; })
        .attr("y2", function(d) { return d.target.y; })
        .style("opacity",function(d) {
            var to_link = (d.target.id == current_video_id);
            var from_link = (d.source.id == current_video_id);
            if (to_link) {
                return 0.2
            }
            if (from_link) {
                return 1
            }
            return 0.5
        })
        .style("stroke", function(d) {
            var to_link = (d.target.id == current_video_id);
            var from_link = (d.source.id == current_video_id);
            if (to_link) {
                return "red"
            }
            if (from_link) {
                return "green"
            }
            return "lightgrey"
        });

    node
        .attr("r", function(d) { return Math.pow(d.views, 0.25)/3 + NODE_MIN_SIZE})
        .attr("cx", function(d) { return d.x; })
        .attr("cy", function(d) { return d.y; })
//        .style("opacity", function(d) {return videos[d.id].accessibility})
}

function make_embeded_link(video_id) {
    return 'https://www.youtube.com/embed/' + video_id;
}
function make_youtube_link(video_id) {
    return 'https://www.youtube.com/watch?v=' + video_id;
}



function update_video_iframe(d) {
    show_video(d)
    recompute_sizes(d.id)
    show_info_bar(d)
    current_video_id = d.id
}
function show_video(d) {
    var link = make_embeded_link(d.id);
    if (document.getElementById("video").getAttribute('src') != link) {
        document.getElementById('video').setAttribute('src', link)
    }
}

function dragstarted(d) {
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
}

function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
}

function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
}

function zoomed() {
    svg2.attr("transform", d3.event.transform);
    ticked()
}

function getHashParams() {
    params = [window.location.hash.replace('#', '')];
    if (!params[0]) {
        // If no parameters, we put both searches for trump and clinton
        params = ['clinton'];
    }

    $('#' + params[0]).addClass('btn-info');
    return params
}

function read_graph() {
    // STEP 1 : get all videos
    var video_names = getHashParams();

    number_of_files = video_names.length;
    number_of_files_read = 0;
    for (var i = 0; i < video_names.length ; i++) {
        var my_json;
        $.getJSON('../video-infos-' + video_names[i] + '.json', function (all_videos) {
            for (var video_id in all_videos) {
                if (all_videos.hasOwnProperty(video_id)) {
                    videos[video_id] = all_videos[video_id];
                    videos[video_id].size = 0;
                    video_list.push(video_id)
                }
            }
            number_of_files_read += 1;
            if (number_of_files_read == number_of_files) {
                var total = 0;
                for (var video_id in videos) {
                    if (all_videos.hasOwnProperty(video_id)) {
                        total++;
                    }
                }
                build_graph(20)
            }
        });
    }
}

var graph = {'nodes': [], 'links': []};

function is_mature(video) {
    return video['likes'] > MIN_NUMBER_OF_LIKES
}

function simulate_trial_from(base_video, depth, weight) {
    videos[base_video].accessibility += weight;
    if (depth > 0) {
        for (var i = 0; i<20; i++) {
            simulate_deeper_if_possible(base_video, depth, i, weight);
        }
    }
}

function simulate_deeper_if_possible(base_video, depth , index, weight) {
    if (videos.hasOwnProperty(base_video) && videos.hasOwnProperty(videos[base_video].recommendations[index])) {
        simulate_trial_from(videos[base_video].recommendations[index], depth - 1, weight)
    }
}

function recompute_sizes(init_video) {
    for (var i=0; i < video_list.length; i++) {
        videos[video_list[i]].accessibility = 0.15;
    }
    simulate_trial_from(init_video, 1, 1)
}

function load_explaination_modals() {
    $('#infoModal1').modal();
}

function build_graph(max_links) {
    console.log('build graph ');
    var total_video_added = 0;
    for (var video_id in videos) {
        if (videos.hasOwnProperty(video_id)) {
            var video = videos[video_id];
            var popularity = -1;
            if (is_mature(video)) {
                popularity = video['likes'] / (parseFloat(video['likes']) + parseFloat(video['dislikes']) + 1);
                total_video_added += 1;
                graph.nodes.push({'id': video_id,
                    'size': video['size'],
                    'popularity': popularity,
                    'type': 'circle',
                    'likes': video['likes'],
                    'dislikes': video['dislikes'],
                    'views': video['views'],
                    'title': video['title'],
                    'accessibility': 1});

                // We only show the first n links to make the graph more visible
                var shown_links = 0;
                for (var i=0; i < video.recommendations.length; i++) {
                    var reco = video.recommendations[i];
                    if (videos.hasOwnProperty(reco) && is_mature(videos[reco]) && shown_links < max_links) {
                        graph.links.push({'source': video_id, 'target': reco, 'value': 1});
                        shown_links++;
                    }
                }
            }
        }
    }
    console.log('The Number of videos for this Graph is: ' + total_video_added);
    display_graph(graph);
    print_videos_name_link_view_count();
}

function print_videos_name_link_view_count() {
    console.log('Now printing all videos sorted by number of views');
    var sorted = new Array()
    for (var video_id in videos) {
        if (videos.hasOwnProperty(video_id)) {
            var video = videos[video_id];
            sorted.push({'id': video_id, 'views': video['views']})
        }
    }
    var real_sorted = sorted.sort(function(a, b) {
        return b['views'] - a['views'];
    });
    for (var i=0; i<real_sorted.length; i++) {
        var video =  videos[real_sorted[i]['id']];
        console.log('<a href="' + make_youtube_link(real_sorted[i]['id']) + '" >' + video['title'] + '</a>: ' + video['views'] + ' views')
    }
}

function select_graph(e) {
    e = e || window.event;
    e = e.target || e.srcElement;
    window.location.href = 'index.html#' + e.id;
    setTimeout("location.reload();", 500);
}


function select_graph(e) {
    // Selecting the graph from the button id.
    e = e || window.event;
    e = e.target || e.srcElement;
    window.location.href = 'index.html#' + e.id;
    setTimeout("location.reload();", 500);
}

function show_info_bar(d) {
    $('.info-bar').show();
    $('.info-bar').html('<strong>' + d.title + '</strong>')
}

function hide_info_bar() {
    $('.info-bar').hide();
    for (var i=0; i < video_list.length; i++) {
        videos[video_list[i]].accessibility = 1;
    }
    ticked()
}

read_graph();
