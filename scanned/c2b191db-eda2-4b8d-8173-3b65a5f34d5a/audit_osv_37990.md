# [M] RAUC: Improper Signing of Plain Bundles Exceeding 2 GiB

## Summary
Severity: Medium
Advisory: CVE-2026-34155
Aliases: GHSA-6hj7-q844-m2hx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:L/VI:H/VA:N/SC:H/SI:H/SA:H)
Published: 2026-03-31
Source: https://osv.dev/vulnerability/CVE-2026-34155
Type: osv

## Details
RAUC controls the update process on embedded Linux systems. Prior to version 1.15.2, RAUC bundles using the 'plain' format exceeding a payload size of 2 GiB cause an integer overflow which results in a signature which covers only the first few bytes of the payload. Given such a bundle with a legitimate signature, an attacker can modify the part of the payload which is not covered by the signature. This issue has been patched in version 1.15.2.

## References
- https://github.com/rauc/rauc/releases/tag/v1.15.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34155.json
- https://github.com/rauc/rauc/security/advisories/GHSA-6hj7-q844-m2hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-34155
- https://github.com/rauc/rauc/commit/4fb7c798d6ae412344fb8f8d310d773046af3441
