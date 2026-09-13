# [M] uutils coreutils has an Uncaught Exception When Encountering Valid but Non-UTF-8 Paths

## Summary
Severity: Medium
Advisory: GHSA-f2jv-wjjc-2c94
CVE: CVE-2026-35348
CWE: CWE-248
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-f2jv-wjjc-2c94
Type: github-advisory

## Affected
- crates.io: `coreutils` — affected >=0

## Details
The sort utility in uutils coreutils is vulnerable to a process panic when using the --files0-from option with inputs containing non-UTF-8 filenames. The implementation enforces UTF-8 encoding and utilizes expect(), causing an immediate crash when encountering valid but non-UTF-8 paths. This diverges from GNU sort, which treats filenames as raw bytes. A local attacker can exploit this to crash the utility and disrupt automated pipelines.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-35348
- https://github.com/uutils/coreutils/issues/9696
- https://github.com/uutils/coreutils
