# [M] PEAR Has a Predictable Verification Hash in Election Account Requests

## Summary
Severity: Medium
Advisory: CVE-2026-25235
Aliases: GHSA-477r-4cmw-3cgf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2026-25235
Type: osv

## Details
PEAR is a framework and distribution system for reusable PHP components. Prior to version 1.33.0, predictable verification hashes may allow attackers to guess verification tokens and potentially verify election account requests without authorization. This issue has been patched in version 1.33.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25235.json
- https://github.com/pear/pearweb/security/advisories/GHSA-477r-4cmw-3cgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-25235
