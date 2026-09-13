# [C] CVE-2018-4056

## Summary
Severity: Critical
Advisory: CVE-2018-4056
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/CVE-2018-4056
Type: osv

## Details
An exploitable SQL injection vulnerability exists in the administrator web portal function of coTURN prior to version 4.5.0.9. A login message with a specially crafted username can cause an SQL injection, resulting in authentication bypass, which could give access to the TURN server administrator web portal. An attacker can log in via the external interface of the TURN server to trigger this vulnerability.

## References
- https://lists.debian.org/debian-lts-announce/2019/02/msg00017.html
- https://www.debian.org/security/2019/dsa-4373
- https://talosintelligence.com/vulnerability_reports/TALOS-2018-0730
