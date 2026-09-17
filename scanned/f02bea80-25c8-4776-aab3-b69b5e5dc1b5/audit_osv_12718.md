# [C] CVE-2018-14473

## Summary
Severity: Critical
Advisory: CVE-2018-14473
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-08-04
Source: https://osv.dev/vulnerability/CVE-2018-14473
Type: osv

## Details
OCS Inventory 2.4.1 lacks a proper XML parsing configuration, allowing the use of external entities. This issue can be exploited by an attacker sending a crafted HTTP request in order to exfiltrate information or cause a Denial of Service.

## References
- https://www.tarlogic.com/en/blog/vulnerabilities-in-ocs-inventory-2-4-1/
