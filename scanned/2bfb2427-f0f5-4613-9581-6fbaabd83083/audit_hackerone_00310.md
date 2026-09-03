# [M] [https-proxy-agent] Socket returned without TLS upgrade on non-200 CONNECT response, allowing request data to be sent over unencrypted connection

## Summary
Severity: Medium (CVSS 6.1)
Program: Node.js third-party modules
Weakness: Man-in-the-Middle
Reporter: kadler15
State: resolved
Disclosed: 2019-09-25T08:21:57.569Z
Source: https://hackerone.com/reports/541502

## Details
I would like to report a man-in-the-middle vulnerability in `https-proxy-agent`.
It allows an attacker with access to the network firewall or targeted proxy server to obtain secrets (e.g. a HTTP basic auth header) from the client trying to send HTTPS traffic via HTTP proxy.

# Module

**module name:** `https-proxy-agent`
**version:** 2.2.1
**npm page:** `https://www.npmjs.com/package/https-proxy-agent`

## Module Description

> This module provides an http.Agent implementation that connects to a specified HTTP or HTTPS proxy server, and can be used with the built-in https module.

## Module Stats

4314908 downloads in the last week

# Vulnerability

## Vulnerability Description

When targeting a HTTP proxy, `https-proxy-agent` [opens a socket](https://github.com/TooTallNate/node-https-proxy-agent/blob/2.2.1/index.js#L77) to the proxy, and sends the proxy server a [CONNECT request](https://github.com/TooTallNate/node-https-proxy-agent/blob/2.2.1/index.js#L203). E.g.:

```
CONNECT www.google.com:443 HTTP/1.1
Host: www.google.com
Connection: close
```

If the proxy server responds with 200 and the client is targeting a secure endpoint, `https-proxy-agent` [TLS-upgrades](https://github.com/TooTallNate/node-https-proxy-agent/blob/2.2.1/index.js#L154) the socket before returning it for use. This is normal and expected.

However, if the proxy server (or firewall blocking the request) responds with something other than a 200, `https-proxy-agent` incorrectly [returns the socket](https://github.com/TooTallNate/node-https-proxy-agent/blob/2.2.1/index.js#L170) without any TLS upgrade. Companion library `agent-base` [passes the socket off](https://github.com/TooTallNate/node-agent-base/blob/4.2.1/index.js#L141) to Node HTTP internals, which will write the pending request data to the socket. E.g.:

```
GET / HTTP/1.1
Host: www.google.com
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
Connection: close
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/541502_
