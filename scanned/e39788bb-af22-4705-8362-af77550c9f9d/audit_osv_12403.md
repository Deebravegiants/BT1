# [M] CVE-2018-1172

## Summary
Severity: Medium
Advisory: CVE-2018-1172
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-16
Source: https://osv.dev/vulnerability/CVE-2018-1172
Type: osv

## Details
This vulnerability allows remote attackers to deny service on vulnerable installations of The Squid Software Foundation Squid 3.5.27-20180318. Authentication is not required to exploit this vulnerability. The specific flaw exists within ClientRequestContext::sslBumpAccessCheck(). A crafted request can trigger the dereference of a null pointer. An attacker can leverage this vulnerability to create a denial-of-service condition to users of the system. Was ZDI-CAN-6088.

## References
- http://www.squid-cache.org/Advisories/SQUID-2018_3.txt
- https://zerodayinitiative.com/advisories/ZDI-18-309
