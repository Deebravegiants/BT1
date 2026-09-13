# [H] CVE-2024-48991

## Summary
Severity: High
Advisory: CVE-2024-48991
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-48991
Type: osv

## Details
Qualys discovered that needrestart, before version 3.8, allows local attackers to execute arbitrary code as root by winning a race condition and tricking needrestart into running their own, fake Python interpreter (instead of the system's real Python interpreter). The initial security fix (6ce6136) introduced a regression which was subsequently resolved (42af5d3).

## References
- http://seclists.org/fulldisclosure/2024/Nov/17
- http://www.openwall.com/lists/oss-security/2024/11/30/4
- https://lists.debian.org/debian-lts-announce/2024/11/msg00014.html
- https://www.openwall.com/lists/oss-security/2024/11/19/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/48xxx/CVE-2024-48991.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-48991
- https://www.qualys.com/2024/11/19/needrestart/needrestart.txt
- https://www.cve.org/CVERecord?id=CVE-2024-48991
- https://github.com/liske/needrestart/commit/42af5d328901287a4f79d1f5861ac827a53fd56d
- https://github.com/liske/needrestart/commit/6ce6136cccc307c6b8a0f8cae12f9a22ac2aad59
- https://github.com/liske/needrestart
