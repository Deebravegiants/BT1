# [M] esbuild enables any website to send any requests to the development server and read the response

## Summary
Severity: Medium
Advisory: GHSA-67mh-4wv8-2f99
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-02-10
Source: https://github.com/advisories/GHSA-67mh-4wv8-2f99
Type: github-advisory

## Affected
- npm: `esbuild` — affected >=0 <0.25.0

## Details
### Summary

esbuild allows any websites to send any request to the development server and read the response due to default CORS settings.

### Details

esbuild sets `Access-Control-Allow-Origin: *` header to all requests, including the SSE connection, which allows any websites to send any request to the development server and read the response.

https://github.com/evanw/esbuild/blob/df815ac27b84f8b34374c9182a93c94718f8a630/pkg/api/serve_other.go#L121
https://github.com/evanw/esbuild/blob/df815ac27b84f8b34374c9182a93c94718f8a630/pkg/api/serve_other.go#L363

**Attack scenario**:

1. The attacker serves a malicious web page (`http://malicious.example.com`).
1. The user accesses the malicious web page.
1. The attacker sends a `fetch('http://127.0.0.1:8000/main.js')` request by JS in that malicious web page. This request is normally blocked by same-origin policy, but that's not the case for the reasons above.
1. The attacker gets the content of `http://127.0.0.1:8000/main.js`.

In this scenario, I assumed that the attacker knows the URL of the bundle output file name. But the attacker can also get that information by

- Fetching `/index.html`: normally you have a script tag here
- Fetching `/assets`: it's common to have a `assets` directory when you have JS files and CSS files in a different directory and the directory listing feature tells the attacker the list of files
- Connecting `/esbuild` SSE endpoint: the SSE endpoint sends the URL path of the changed files when the file is changed (`new EventSource('/esbuild').addEventListener('change', e => console.log(e.type, e.data))`)
- Fetching URLs in the known file: once the attacker knows one file, the attacker can know the URLs imported from that file

The scenario above fetches the compiled content, but if the victim has the source map option enabled, the attacker can also get the non-compiled content by fetching the source map file.

### PoC

1. Download [reproduction.zip](https://github.com/user-attachments/files/18561484/reproduction.zip)
2. Extract it and move to that directory
1. Run `npm i`
1. Run `npm run watch`
1. Run `fetch('http://127.0.0.1:8000/app.js').then(r => r.text()).then(content => console.log(content))` in a different website's dev tools.

![image](https://github.com/user-attachments/assets/08fc2e4d-e1ec-44ca-b0ea-78a73c3c40e9)

### Impact

Users using the serve feature may get the source code stolen by malicious websites.

## References
- https://github.com/evanw/esbuild/security/advisories/GHSA-67mh-4wv8-2f99
- https://github.com/evanw/esbuild/commit/de85afd65edec9ebc44a11e245fd9e9a2e99760d
- https://github.com/evanw/esbuild
