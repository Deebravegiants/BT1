# [C] CVE-2017-12087

## Summary
Severity: Critical
Advisory: CVE-2017-12087
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-04-24
Source: https://osv.dev/vulnerability/CVE-2017-12087
Type: osv

## Details
An exploitable heap overflow vulnerability exists in the tinysvcmdns library version 2016-07-18. A specially crafted packet can make the library overwrite an arbitrary amount of data on the heap with attacker controlled values. An attacker needs send a dns packet to trigger this vulnerability.

## References
- https://www.talosintelligence.com/vulnerability_reports/TALOS-2017-0439
