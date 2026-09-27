# [C] CVE-2022-37623

## Summary
Severity: Critical
Advisory: CVE-2022-37623
Aliases: GHSA-cfgr-75jx-h88g
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-31
Source: https://osv.dev/vulnerability/CVE-2022-37623
Type: osv

## Details
Prototype pollution vulnerability in function resolveShims in resolve-shims.js in thlorenz browserify-shim 3.8.15 via the shimPath variable in resolve-shims.js.

## References
- https://github.com/thlorenz/browserify-shim/blob/464b32bbe142664cd9796059798f6c738ea3de8f/lib/resolve-shims.js#L158
- https://github.com/thlorenz/browserify-shim/blob/464b32bbe142664cd9796059798f6c738ea3de8f/lib/resolve-shims.js#L94
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37623.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37623
- https://github.com/thlorenz/browserify-shim/issues/248
