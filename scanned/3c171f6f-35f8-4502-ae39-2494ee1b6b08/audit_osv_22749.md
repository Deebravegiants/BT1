# [C] CVE-2022-37621

## Summary
Severity: Critical
Advisory: CVE-2022-37621
Aliases: GHSA-r737-347m-wqc7
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-28
Source: https://osv.dev/vulnerability/CVE-2022-37621
Type: osv

## Details
Prototype pollution vulnerability in function resolveShims in resolve-shims.js in thlorenz browserify-shim 3.8.15 via the fullPath variable in resolve-shims.js.

## References
- https://github.com/thlorenz/browserify-shim/blob/464b32bbe142664cd9796059798f6c738ea3de8f/lib/resolve-shims.js#L158
- https://github.com/thlorenz/browserify-shim/blob/464b32bbe142664cd9796059798f6c738ea3de8f/lib/resolve-shims.js#L37
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/37xxx/CVE-2022-37621.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-37621
- https://github.com/thlorenz/browserify-shim/issues/247
