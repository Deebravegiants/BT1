# [M] Websites were able to send any requests to the development server and read the response in vite

## Summary
Severity: Medium
Advisory: GHSA-vg6x-rcgg-rjx6
CVE: CVE-2025-24010
CWE: CWE-1385, CWE-346, CWE-350
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-vg6x-rcgg-rjx6
Type: github-advisory

## Affected
- npm: `vite` — affected >=6.0.0 <6.0.9
- npm: `vite` — affected >=5.0.0 <5.4.12
- npm: `vite` — affected >=0 <4.5.6

## Details
### Summary
Vite allowed any websites to send any requests to the development server and read the response due to default CORS settings and lack of validation on the Origin header for WebSocket connections.

> [!WARNING]
> This vulnerability even applies to users that only run the Vite dev server on the local machine and does not expose the dev server to the network.

### Upgrade Path
Users that does not match either of the following conditions should be able to upgrade to a newer version of Vite that fixes the vulnerability without any additional configuration.

- Using the backend integration feature
- Using a reverse proxy in front of Vite
- Accessing the development server via a domain other than `localhost` or `*.localhost`
- Using a plugin / framework that connects to the WebSocket server on their own from the browser

#### Using the backend integration feature
If you are using the backend integration feature and not setting [`server.origin`](https://vite.dev/config/server-options.html#server-origin), you need to add the origin of the backend server to the [`server.cors.origin`](https://github.com/expressjs/cors#configuration-options) option. Make sure to set a specific origin rather than `*`, otherwise any origin can access your development server.

#### Using a reverse proxy in front of Vite
If you are using a reverse proxy in front of Vite and sending requests to Vite with a hostname other than `localhost` or `*.localhost`, you need to add the hostname to the new [`server.allowedHosts`](https://vite.dev/config/server-options.html#server-allowedhosts) option. For example, if the reverse proxy is sending requests to `http://vite:5173`, you need to add `vite` to the `server.allowedHosts` option.

#### Accessing the development server via a domain other than `localhost` or `*.localhost`
You need to add the hostname to the new [`server.allowedHosts`](https://vite.dev/config/server-options.html#server-allowedhosts) option. For example, if you are accessing the development server via `http://foo.example.com:8080`, you need to add `foo.example.com` to the `server.allowedHosts` option.

#### Using a plugin / framework that connects to the WebSocket server on their own from the browser
If you are using a plugin / framework, try upgrading to a newer version of Vite that fixes the vulnerability. If the WebSocket connection appears not to be working, the plugin / framework may have a code that connects to the WebSocket server on their own from the browser.

In that case, you can either:

- fix the plugin / framework code to the make it compatible with the new version of Vite
- set `legacy.skipWebSocketTokenCheck: true` to opt-out the fix for [2] while the plugin / framework is incompatible with the new version of Vite
  - When enabling this option, **make sure that you are aware of the security implications** described in the impact section of [2] above.

### Mitigation without upgrading Vite
#### [1]: Permissive default CORS settings
Set `server.cors` to `false` or limit `server.cors.origin` to trusted origins.

#### [2]: Lack of validation on the Origin header for WebSocket connections
There aren't any mitigations for this.

#### [3]: Lack of validation on the Host header for HTTP requests
Use Chrome 94+ or use HTTPS for the development server.

### Details

There are three causes that allowed malicious websites to send any requests to the development server:

#### [1]: Permissive default CORS settings

Vite sets the [`Access-Control-Allow-Origin`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin) header depending on [`server.cors`](https://vite.dev/config/server-options.html#server-cors) option. The default value was `true` which sets `Access-Control-Allow-Origin: *`. This allows websites on any origin to `fetch` contents served on the development server.

Attack scenario:

1. The attacker serves a malicious web page (`http://malicious.example.com`).
2. The user accesses the malicious web page.
3. The attacker sends a `fetch('http://127.0.0.1:5173/main.js')` request by JS in that malicious web page. This request is normally blocked by same-origin policy, but that's not the case for the reasons above.
4. The attacker gets the content of `http://127.0.0.1:5173/main.js`.

#### [2]: Lack of validation on the Origin header for WebSocket connections

Vite starts a WebSocket server to handle HMR and other functionalities. This WebSocket server [did not perform validation on the Origin header](https://github.com/vitejs/vite/blob/v6.0.7/packages/vite/src/node/server/ws.ts#L145-L157) and was vulnerable to Cross-Site WebSocket Hijacking (CSWSH) attacks. With that attack, an attacker can read and write messages on the WebSocket connection. Vite only sends some information over the WebSocket connection ([list of the file paths that changed, the file content where the errored happened, etc.](https://github.com/vitejs/vite/blob/v6.0.7/packages/vite/types/hmrPayload.d.ts#L12-L72)), but plugins can send arbitrary messages and may include more sensitive information.

Attack scenario:

1. The attacker serves a malicious web page (`http://malicious.example.com`).
2. The user accesses the malicious web page.
3. The attacker runs `new WebSocket('http://127.0.0.1:5173', 'vite-hmr')` by JS in that malicious web page.
4. The user edits some files.
5. Vite sends some HMR messages over WebSocket.
6. The attacker gets the content of the HMR messages.

#### [3]: Lack of validation on the Host header for HTTP requests

Unless [`server.https`](https://vite.dev/config/server-options.html#server-https) is set, Vite starts the development server on HTTP. Non-HTTPS servers are vulnerable to DNS rebinding attacks without validation on the Host header. But Vite did not perform validation on the Host header. By exploiting this vulnerability, an attacker can send arbitrary requests to the development server bypassing the same-origin policy.

1. The attacker serves a malicious web page that is served on **HTTP** (`http://malicious.example.com:5173`) (HTTPS won't work).
2. The user accesses the malicious web page.
3. The attacker changes the DNS to point to 127.0.0.1 (or other private addresses).
4. The attacker sends a `fetch('/main.js')` request by JS in that malicious web page.
5. The attacker gets the content of `http://127.0.0.1:5173/main.js` bypassing the same origin policy.

### Impact
#### [1]: Permissive default CORS settings
Users with the default `server.cors` option may:

- get the source code stolen by malicious websites
- give the attacker access to functionalities that are not supposed to be exposed externally
  - Vite core does not have any functionality that causes changes somewhere else when receiving a request, but plugins may implement those functionalities and servers behind `server.proxy` may have those functionalities.

#### [2]: Lack of validation on the Origin header for WebSocket connections
All users may get the file paths of the files that changed and the file content where the error happened be stolen by malicious websites.

For users that is using a plugin that sends messages over WebSocket, that content may be stolen by malicious websites.

For users that is using a plugin that has a functionality that is triggered by messages over WebSocket, that functionality may be exploited by malicious websites.

#### [3]: Lack of validation on the Host header for HTTP requests
Users using HTTP for the development server and using a browser that is not Chrome 94+ may:

- get the source code stolen by malicious websites
- give the attacker access to functionalities that are not supposed to be exposed externally
  - Vite core does not have any functionality that causes changes somewhere else when receiving a request, but plugins may implement those functionalities and servers behind `server.proxy` may have those functionalities.

Chrome 94+ users are not affected for [3], because [sending a request to a private network page from public non-HTTPS page is forbidden](https://developer.chrome.com/blog/private-network-access-update#chrome_94) since Chrome 94.

### Related Information
Safari has [a bug that blocks requests to loopback addresses from HTTPS origins](https://bugs.webkit.org/show_bug.cgi?id=171934). This means when the user is using Safari and Vite is listening on lookback addresses, there's another condition of "the malicious web page is served on HTTP" to make [1] and [2] to work.

### PoC
#### [2]: Lack of validation on the Origin header for WebSocket connections
1. I used the `react` template which utilizes HMR functionality.

```
npm create vite@latest my-vue-app-react -- --template react
```

2. Then on a malicious server, serve the following POC html:
```html
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>vite CSWSH</title>
    </head>
    <body>
        <div id="logs"></div>
        <script>
            const div = document.querySelectorAll('#logs')[0];
            const ws = new WebSocket('ws://localhost:5173','vite-hmr');
            ws.onmessage = event => {
                const logLine = document.createElement('p');
                logLine.innerHTML = event.data;
                div.append(logLine);
            };
        </script>
    </body>
</html>
```

3. Kick off Vite 

```
npm run dev
```

4. Load the development server (open `http://localhost:5173/`) as well as the malicious page in the browser. 
5. Edit `src/App.jsx` file and intentionally place a syntax error
6. Notice how the malicious page can view the websocket messages and a snippet of the source code is exposed

Here's a video demonstrating the POC:

https://github.com/user-attachments/assets/a4ad05cd-0b34-461c-9ff6-d7c8663d6961

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-vg6x-rcgg-rjx6
- https://nvd.nist.gov/vuln/detail/CVE-2025-24010
- https://github.com/vitejs/vite
