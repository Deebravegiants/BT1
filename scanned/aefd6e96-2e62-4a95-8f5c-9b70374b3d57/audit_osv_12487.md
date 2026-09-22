# [H] CVE-2018-12483

## Summary
Severity: High
Advisory: CVE-2018-12483
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-04
Source: https://osv.dev/vulnerability/CVE-2018-12483
Type: osv

## Details
OCS Inventory 2.4.1 is prone to a remote command-execution vulnerability. Specifically, this issue occurs because the content of the ipdiscover_analyser rzo GET parameter is concatenated to a string used in an exec() call in the PHP code. Authentication is needed in order to exploit this vulnerability.

## References
- https://www.tarlogic.com/en/blog/vulnerabilities-in-ocs-inventory-2-4-1/
