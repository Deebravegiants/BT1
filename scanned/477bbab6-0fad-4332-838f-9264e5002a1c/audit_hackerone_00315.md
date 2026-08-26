# [H] Multiple HTTP/2 DOS Issues

## Summary
Severity: High
Program: Node.js
Weakness: Uncontrolled Resource Consumption
Reporter: jasnell
State: resolved
Disclosed: 2019-08-16T23:40:09.482Z
Source: https://hackerone.com/reports/589739

## Details
A security researcher has conducted a broad survey of HTTP/2 implementations to investigate common Denial of Service attack vectors. The Node.js implementation has been found to be subject to a number of these issues. (On the plus side, we're not the only ones! ;-) ...)

This work is still under embargo and has not yet been disclosed. 

Specifically:

* Data Dribble Attack: "This program will request 1MB of data from a specified resource. It will request this same resource over 100 streams (so, 100MB total). It manipulates window sizes and stream priority to force the server to queue the data in 1-byte chunks."

* Ping Flood (nginx variant):  "Nginx and libnghttp2 (used by Apache, Tomcat, node.js, and others) has a 10K-message limit on the number of control messages it will queue. Sending a controlled number of messages may enable an attacker to force the server to hold 10K messages in memory..."

* Resource Loop: "(actually, it should be called “Priority Shuffling”): This program continually shuffles the priority of streams in a way which causes substantial churn to the priority tree. Node.js [is] particularly impacted."

* Reset Flood: "This opens a number of streams and sends an invalid request over each stream. In some servers, this solicits a string of stream RSTs. In [Node.js] the servers may queue the RSTs internally until they run out of memory."

* O-Length Headers Leak: "This sends a stream of headers with a 0-length header name and 0-length header value. [Node.js] allocates memory for these headers and keeps the allocation alive until the session dies. Because the names and values are 0 bytes long, the cumulative length never exceeds the header size limit."

* Internal Data Buffering: "This opens the HTTP/2 window so the server can send without constraint; however, it leaves the TCP window closed so the server cannot actually write (many of) the bytes on the wire. Then, the client sends a stream of requests for a large response object which the target queues internally. This appears to work to create a long-ish standing queue in node.js"

Each is a distinct issue that will need to be looked at individually. I've edited the descriptions to remove references to vulnerabilities in other HTTP/2 implementations that have not yet been disclosed.

---

Additional details from the report:

```
“Data Dribble” on node.js: node.js seems to queue the data internally. For a 1MB output file
requested 100 times in parallel fast enough that node.js is constantly processing input,
node.js’s RSS rises by 808MB and then falls by 120MB (for an aggregate rise of 688MB).
(Actually, it looks like the numbers vary a bit across tests, but I think the end result is “a lot”.)
However, node.js does not have the excess CPU utilization which Nginx exhibits. If you
instead delay the sends considerably so that node.js has time to try to send in the meantime, it
looks like node.js will kill off the session before the input queue grows more than a few
hundred MB.

“Internal Data Buffering” on node.js: For a 1MB output file requested 100 times in parallel
(but sent with 24 requests per SSL frame), node.js behaves in an interesting way. It appears to
buffer some, but not all, data internally. It seems to continue reading (and processing requests
and queueing data to satisfy those requests) for as many streams as it can until it can’t read
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/589739_
