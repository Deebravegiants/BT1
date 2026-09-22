# [H] netavark has incorrect error handling for malformed tcp packets

## Summary
Severity: High
Advisory: GHSA-hfpq-x728-986j
CVE: CVE-2026-35406
CWE: CWE-400, CWE-835
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-07
Source: https://github.com/advisories/GHSA-hfpq-x728-986j
Type: github-advisory

## Affected
- crates.io: `netavark` — affected >=1.16.0 <1.17.1

## Details
### Impact

A truncated TCP DNS query followed by a connection reset causes aardvark-dns to enter an unrecoverable infinite error loop at 100% CPU.

### Patches
https://github.com/containers/aardvark-dns/commit/3b49ea7b38bdea134b7f03256f2e13f44ce73bb1

### Workarounds
None

### Credits

Thanks to @dkane01 for reporting this

## References
- https://github.com/containers/aardvark-dns/security/advisories/GHSA-hfpq-x728-986j
- https://nvd.nist.gov/vuln/detail/CVE-2026-35406
- https://github.com/containers/aardvark-dns/commit/3b49ea7b38bdea134b7f03256f2e13f44ce73bb1
- https://github.com/containers/aardvark-dns
- https://github.com/containers/aardvark-dns/releases/tag/v1.17.1
