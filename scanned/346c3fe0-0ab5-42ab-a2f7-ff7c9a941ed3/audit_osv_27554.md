# [C] CVE-2024-23771

## Summary
Severity: Critical
Advisory: CVE-2024-23771
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-22
Source: https://osv.dev/vulnerability/CVE-2024-23771
Type: osv

## Details
darkhttpd before 1.15 uses strcmp (which is not constant time) to verify authentication, which makes it easier for remote attackers to bypass authentication via a timing side channel.

## References
- https://github.com/emikulic/darkhttpd/compare/v1.14...v1.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/23xxx/CVE-2024-23771.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-23771
- https://github.com/emikulic/darkhttpd/commit/f477619d49f3c4de9ad59bd194265a48ddc03f04
- http://www.openwall.com/lists/oss-security/2024/01/25/1
