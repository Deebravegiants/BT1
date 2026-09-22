# [M] CVE-2026-87724

## Summary
Severity: Medium
Advisory: CVE-2026-87724
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87724
Type: osv

## Details
Tor before 0.4.9.12 interprets the CC_RESPONSE extension even when CC_REQUEST was not sent, which allows remote attackers to cause a denial of service (crash) because of corrupted congestion-control state. This is TROVE-2026-032.

## References
- https://gitlab.torproject.org/tpo/core/tor/-/raw/tor-0.4.9.12/ChangeLog
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87724.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-87724
- https://gitlab.com/torproject/tor/-/commit/10d4b8ffefa7c00aab2b631ed7e7f15e42cd012d
