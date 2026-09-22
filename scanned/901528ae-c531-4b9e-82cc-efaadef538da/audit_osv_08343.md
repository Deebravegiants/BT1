# [C] CVE-2016-2339

## Summary
Severity: Critical
Advisory: CVE-2016-2339
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2339
Type: osv

## Details
An exploitable heap overflow vulnerability exists in the Fiddle::Function.new "initialize" function functionality of Ruby. In Fiddle::Function.new "initialize" heap buffer "arg_types" allocation is made based on args array length. Specially constructed object passed as element of args array can increase this array size after mentioned allocation and cause heap overflow.

## References
- http://www.securityfocus.com/bid/91234
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- http://www.talosintelligence.com/reports/TALOS-2016-0034/
