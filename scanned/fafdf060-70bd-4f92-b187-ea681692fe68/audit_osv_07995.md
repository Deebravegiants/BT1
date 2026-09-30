# [H] CVE-2016-0896

## Summary
Severity: High
Advisory: CVE-2016-0896
CVSS: 7.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2016-09-18
Source: https://osv.dev/vulnerability/CVE-2016-0896
Type: osv

## Details
Pivotal Cloud Foundry (PCF) Elastic Runtime before 1.6.34 and 1.7.x before 1.7.12 places 169.254.0.0/16 in the all_open Application Security Group, which might allow remote attackers to bypass intended network-connectivity restrictions by leveraging access to the 169.254.169.254 address.

## References
- http://www.securityfocus.com/bid/92161
- https://pivotal.io/security/cve-2016-0896
