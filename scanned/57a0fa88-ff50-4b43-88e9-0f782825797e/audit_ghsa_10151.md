# [M] Vite Vulnerable to Path Traversal in Optimized Deps `.map` Handling

## Summary
Severity: Medium
Advisory: GHSA-4w7w-66w2-5vf9
CVE: CVE-2026-39365
CWE: CWE-200, CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-06
Source: https://github.com/advisories/GHSA-4w7w-66w2-5vf9
Type: github-advisory

## Affected
- npm: `vite` — affected >=8.0.0 <8.0.5
- npm: `vite` — affected >=7.0.0 <7.3.2
- npm: `vite` — affected >=0 <6.4.2

## Details
### Summary

Any files ending with `.map` even out side the project can be returned to the browser.

### Impact

Only apps that match the following conditions are affected:

- explicitly exposes the Vite dev server to the network (using `--host` or [`server.host` config option](https://vitejs.dev/config/server-options.html#server-host))
- have a sensitive content in files ending with `.map` and the path is predictable

### Details

In Vite v7.3.1, the dev server’s handling of `.map` requests for optimized dependencies resolves file paths and calls `readFile` without restricting `../` segments in the URL. As a result, it is possible to bypass the [`server.fs.strict`](https://vite.dev/config/server-options#server-fs-strict) allow list and retrieve `.map` files located outside the project root, provided they can be parsed as valid source map JSON.

### PoC
1. Create a minimal PoC sourcemap outside the project root
    ```bash
    cat > /tmp/poc.map <<'EOF'
    {"version":3,"file":"x.js","sources":[],"names":[],"mappings":""}
    EOF
    ```
2. Start the Vite dev server (example)
    ```bash
    pnpm -C playground/fs-serve dev --host 127.0.0.1 --port 18080
    ```
3. Confirm that direct `/@fs` access is blocked by `strict` (returns 403)
    <img width="4004" height="1038" alt="image" src="https://github.com/user-attachments/assets/15a859a8-1dc6-4105-8d58-80527c0dd9ab" />
4. Inject `../` segments under the optimized deps `.map` URL prefix to reach `/tmp/poc.map`
    <img width="2790" height="846" alt="image" src="https://github.com/user-attachments/assets/5d02957d-2e6a-4c45-9819-3f024e0e81f2" />

## References
- https://github.com/vitejs/vite/security/advisories/GHSA-4w7w-66w2-5vf9
- https://nvd.nist.gov/vuln/detail/CVE-2026-39365
- https://github.com/vitejs/vite/pull/22161
- https://github.com/vitejs/vite/commit/79f002f2286c03c88c7b74c511c7f9fc6dc46694
- https://github.com/vitejs/vite
- https://github.com/vitejs/vite/releases/tag/v6.4.2
- https://github.com/vitejs/vite/releases/tag/v7.3.2
- https://github.com/vitejs/vite/releases/tag/v8.0.5
