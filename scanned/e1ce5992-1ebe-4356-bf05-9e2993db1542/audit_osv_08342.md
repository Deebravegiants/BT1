# [C] CVE-2016-2338

## Summary
Severity: Critical
Advisory: CVE-2016-2338
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-29
Source: https://osv.dev/vulnerability/CVE-2016-2338
Type: osv

## Details
An exploitable heap overflow vulnerability exists in the Psych::Emitter start_document function of Ruby. In Psych::Emitter start_document function heap buffer "head" allocation is made based on tags array length. Specially constructed object passed as element of tags array can increase this array size after mentioned allocation and cause heap overflow.

## References
- https://lists.debian.org/debian-lts-announce/2020/03/msg00032.html
- https://security.netapp.com/advisory/ntap-20221228-0005/
- http://www.talosintelligence.com/reports/TALOS-2016-0032/
