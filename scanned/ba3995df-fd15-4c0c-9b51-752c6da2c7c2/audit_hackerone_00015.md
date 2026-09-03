# [M] HTTP Request Smuggling via Connection: close<TAB> in Node.js llhttp parser

## Summary
Severity: Medium (CVSS 5.8)
Program: Node.js
Weakness: HTTP Request Smuggling
Reporter: nadav0077
State: resolved
Disclosed: 2026-07-31T15:27:19.982Z
Source: https://hackerone.com/reports/3723248

## Details
**Summary:** Node's HTTP server ignores `Connection: close` when the token is followed by a tab character, so bytes after the request body can be parsed as a second request on the same connection.

**Description:** I found a parsing difference in Node's HTTP/1 handling for the `Connection` header.

`Connection: close` works as expected: after the request body, Node does not accept another request on that connection. `Connection: close ` with a trailing space also works as expected.

But `Connection: close\t` behaves differently. Node does not apply the `close` connection option, keeps the connection alive, and parses the bytes immediately after the first request body as another HTTP request. In my test, a single TCP write containing a POST followed by `GET /smuggled` results in the application receiving two request events.

This looks like it comes from llhttp's `Connection` token parser. After recognizing `close`, the parser accepts comma, space, CR, and LF, but not HTAB. The HTAB path falls back in a way that drops the pending `CONNECTION_CLOSE` state.

This looks like it comes from llhttp’s `Connection` token parser. After recognizing `close`, the parser accepts comma, space, CR, and LF, but not HTAB. The HTAB path falls back in a way that drops the pending `CONNECTION_CLOSE` state.

Although the root cause appears to be in llhttp, this report is for Node.js because the behavior is reachable through Node's default `http.createServer()` API with attacker-controlled inbound network data.

Relevant code:

- https://github.com/nodejs/llhttp/blob/main/src/llhttp/http.ts#L794-L826
- https://github.com/nodejs/llhttp/blob/main/src/native/http.c#L156-L169

## Steps To Reproduce

I reproduced this with Node.js v24.13.1, v24.15.0, and v26.1.0 using default `http.createServer()` settings.

### Manual Reproduction Without Script

Terminal 1: start a default Node HTTP server.

```bash
node -e "require('http').createServer((req,res)=>{console.log('request:', req.url); req.resume(); res.end('ok');}).listen(8080,'127.0.0.1',()=>console.log('listening'))"
```

Terminal 2: send the control case with normal `Connection: close`.

```bash
printf 'POST /first HTTP/1.1\r\nHost: victim\r\nContent-Length: 4\r\nConnection: close\r\n\r\n1234GET /smuggled HTTP/1.1\r\nHost: victim\r\n\r\n' | nc -w 2 127.0.0.1 8080
```

Expected server output in Terminal 1:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3723248_
