# [H] Misuse of `Reference` and other transferable APIs may lead to access to nodejs isolate

## Summary
Severity: High
Advisory: GHSA-mmhj-4w6j-76h7
CVE: CVE-2021-21413
CWE: CWE-913
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-06
Source: https://github.com/advisories/GHSA-mmhj-4w6j-76h7
Type: github-advisory

## Affected
- npm: `isolated-vm` — affected >=0 <4.0.0

## Details
Versions of `isolated-vm` before v4.0.0, and especially before v3.0.0, have API pitfalls which may make it easy for implementers to expose supposed secure isolates to the permissions of the main nodejs isolate.

`Reference` objects allow access to the underlying reference's full prototype chain. In an environment where the implementer has exposed a `Reference` instance to an attacker they would be able to use it to acquire a `Reference` to the nodejs context's `Function` object.

Similar application-specific attacks could be possible by modifying the local prototype of other API objects.

Access to `NativeModule` objects could allow an attacker to load and run native code from anywhere on the filesystem. If combined with, for example, a file upload API this would allow for arbitrary code execution.

To address these issues the following changes were made in v4.0.0:
- Documentation was updated with more explicit guidelines on building secure applications.
- `Reference` instances will no longer follow prototype chains by default, nor will they invoke accessors or proxies.
- All `isolated-vm` API prototypes are now immutable.
- `NativeModule` constructor may only be invoked from a nodejs isolate.

## References
- https://github.com/laverdet/isolated-vm/security/advisories/GHSA-mmhj-4w6j-76h7
- https://nvd.nist.gov/vuln/detail/CVE-2021-21413
- https://github.com/laverdet/isolated-vm/commit/2646e6c1558bac66285daeab54c7d490ed332b15
- https://github.com/laverdet/isolated-vm/commit/27151bfecc260e96714443613880e3b2e6596704
- https://github.com/laverdet/isolated-vm/blob/main/CHANGELOG.md#v400
