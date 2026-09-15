# [C] CVE-2016-2336

## Summary
Severity: Critical
Advisory: CVE-2016-2336
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-01-06
Source: https://osv.dev/vulnerability/CVE-2016-2336
Type: osv

## Details
Type confusion exists in two methods of Ruby's WIN32OLE class, ole_invoke and ole_query_interface. Attacker passing different type of object than this assumed by developers can cause arbitrary code execution.

## References
- http://www.talosintelligence.com/reports/TALOS-2016-0029/
