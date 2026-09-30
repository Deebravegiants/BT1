# [C] Sandbox bypass leading to arbitrary code execution in Deno

## Summary
Severity: Critical
Advisory: GHSA-838h-jqp6-cf2f
CVE: CVE-2022-24783
CWE: CWE-269, CWE-863
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-29
Source: https://github.com/advisories/GHSA-838h-jqp6-cf2f
Type: github-advisory

## Affected
- crates.io: `deno` — affected >=1.18.0 <1.20.3

## Details
### Impact

The versions of Deno between release 1.18.0 and 1.20.2 (inclusive) are vulnerable to an attack where a malicious actor controlling the code executed in a Deno runtime could bypass permission checks and execute arbitrary shell code.

There is **no** evidence that this vulnerability has been exploited in the wild.

This vulnerability does **not** affect users of Deno Deploy.

### Patches

The vulnerability has been patched in Deno 1.20.3.

### Workarounds

There is no workaround. All users are recommended to upgrade to 1.20.3 immediately

---

The cause of this error was that certain FFI operations did not correctly check for permissions. The issue was fixed in [this](https://github.com/denoland/deno/pull/14115) pull request.

## References
- https://github.com/denoland/deno/security/advisories/GHSA-838h-jqp6-cf2f
- https://nvd.nist.gov/vuln/detail/CVE-2022-24783
- https://github.com/denoland/deno/pull/14115
- https://github.com/denoland/deno/commit/fcfce1bb869fddc629e6d889d6ba1328b80b0dcf
- https://github.com/denoland/deno
- https://github.com/denoland/deno/compare/v1.20.2...v1.20.3
- https://github.com/denoland/deno/releases/tag/v1.20.3
