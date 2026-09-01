# [H] Assertion failed in node::http2::Http2Session::~Http2Session() leads to HTTP/2 server crash

## Summary
Severity: High (CVSS 7.5)
Program: Internet Bug Bounty
Weakness: Uncontrolled Resource Consumption
Reporter: bart
State: resolved
Disclosed: 2024-04-29T21:01:40.904Z
CVE: CVE-2024-27983
Source: https://hackerone.com/reports/2453328

## Details
An attacker can make the Node.js HTTP/2 server completely unavailable by sending a small amount of HTTP/2 frames packets with a few HTTP/2 frames inside. It is possible to leave some data in nghttp2 memory after reset when headers with HTTP/2 CONTINUATION frame are sent to the server and then a TCP connection is abruptly closed by the client triggering the Http2Session destructor while header frames are still being processed (and stored in memory) causing a race condition.

* Advisory: https://nodejs.org/en/blog/vulnerability/april-2024-security-releases
* HackerOne report: 2319584

## Impact

Server crashes instantly after sending a few HTTP/2 frames.
