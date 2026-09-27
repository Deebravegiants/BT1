# [M] ZX Allows Environment Variable Injection for dotenv API

## Summary
Severity: Medium
Advisory: GHSA-qwp8-x4ff-5h87
CVE: CVE-2025-24959
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-03
Source: https://github.com/advisories/GHSA-qwp8-x4ff-5h87
Type: github-advisory

## Affected
- npm: `zx` — affected >=8.3.1 <8.3.2

## Details
### Impact
This vulnerability is an **Environment Variable Injection** issue in `dotenv.stringify`, affecting `google/zx`  version **8.3.1**.

An attacker with control over environment variable values can inject unintended environment variables into `process.env`. This can lead to **arbitrary command execution** or **unexpected behavior** in applications that rely on environment variables for security-sensitive operations. Applications that process untrusted input and pass it through `dotenv.stringify` are particularly vulnerable.

### Patches
This issue has been **patched** in version **8.3.2**. Users should **immediately upgrade** to this version to mitigate the vulnerability.

### Workarounds
If upgrading is not feasible, users can mitigate the vulnerability by **sanitizing user-controlled environment variable values** before passing them to `dotenv.stringify`. Specifically, avoid using `"`, `'`, and backticks in values, or enforce strict validation of environment variables before usage.

### References
- [Issue Report](https://github.com/google/zx/issues/)
- [Security Policy](https://github.com/google/zx/security/policy)
- [Google Vulnerability Disclosure](https://g.co/vulnz)
- [Patch](https://github.com/google/zx/pull/1094)

## References
- https://github.com/google/zx/security/advisories/GHSA-qwp8-x4ff-5h87
- https://nvd.nist.gov/vuln/detail/CVE-2025-24959
- https://github.com/google/zx/pull/1094
- https://github.com/google/zx/commit/5ba714d14ecf0555a74d4db96622840ac19839c5
- https://github.com/google/zx
- https://github.com/webpod/envapi/blob/v0.2.1/src/main/ts/envapi.ts#L74-L77
