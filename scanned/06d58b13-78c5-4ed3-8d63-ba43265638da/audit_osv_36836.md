# [C] PJSIP has a heap buffer overflow in ICE with long username

## Summary
Severity: Critical
Advisory: CVE-2026-25994
Aliases: GHSA-j29p-pvh2-pvqp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-25994
Type: osv

## Details
PJSIP is a free and open source multimedia communication library written in C. In 2.16 and earlier, a buffer overflow vulnerability exists in PJNATH ICE Session when processing credentials with excessively long usernames.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25994.json
- https://github.com/pjsip/pjproject/security/advisories/GHSA-j29p-pvh2-pvqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-25994
- https://github.com/pjsip/pjproject/commit/063b3a155f163cc5a9a1df2c56b6720fd3a0dbb0
