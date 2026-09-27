# [M] CVE-2019-20917

## Summary
Severity: Medium
Advisory: CVE-2019-20917
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-11
Source: https://osv.dev/vulnerability/CVE-2019-20917
Type: osv

## Details
An issue was discovered in InspIRCd 2 before 2.0.28 and 3 before 3.3.0. The mysql module contains a NULL pointer dereference when built against mariadb-connector-c 3.0.5 or newer. When combined with the sqlauth or sqloper modules, this vulnerability can be used for remote crashing of an InspIRCd server by any user able to connect to a server.

## References
- https://docs.inspircd.org/security/2019-02/
- https://lists.debian.org/debian-lts-announce/2020/09/msg00015.html
- https://www.debian.org/security/2020/dsa-4764
- https://github.com/inspircd/inspircd/commit/2cc35d8625b7ea5cbd1d1ebb116aff86c5280162
- https://github.com/inspircd/inspircd/commit/8745660fcdac7c1b80c94cfc0ff60928cd4dd4b7
