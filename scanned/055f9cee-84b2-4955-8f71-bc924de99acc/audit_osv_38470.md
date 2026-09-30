# [M] Out-of-bounds read in SetMacAddrAction

## Summary
Severity: Medium
Advisory: CVE-2026-40210
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-40210
Type: osv

## Details
An out-of-bounds read might happen when SetMacAddrAction is used, potentially resulting in uninitialized memory being sent over the network or a crash.

## References
- https://repo.powerdns.com/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40210.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40210
- https://www.dnsdist.org/security-advisories/powerdns-advisory-for-dnsdist-2026-09.html
- https://github.com/PowerDNS/pdns
