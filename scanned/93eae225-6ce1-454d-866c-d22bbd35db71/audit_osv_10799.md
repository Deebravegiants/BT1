# [C] CVE-2017-2801

## Summary
Severity: Critical
Advisory: CVE-2017-2801
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-2801
Type: osv

## Details
A programming error exists in a way Randombit Botan cryptographic library version 2.0.1 implements x500 string comparisons which could lead to certificate verification issues and abuse. A specially crafted X509 certificate would need to be delivered to the client or server application in order to trigger this vulnerability.

## References
- http://www.debian.org/security/2017/dsa-3939
- http://www.securityfocus.com/bid/98106
- http://talosintelligence.com/vulnerability_reports/TALOS-2017-0294
