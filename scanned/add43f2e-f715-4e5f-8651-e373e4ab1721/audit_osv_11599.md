# [H] CVE-2017-9023

## Summary
Severity: High
Advisory: CVE-2017-9023
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/CVE-2017-9023
Type: osv

## Details
The ASN.1 parser in strongSwan before 5.5.3 improperly handles CHOICE types when the x509 plugin is enabled, which allows remote attackers to cause a denial of service (infinite loop) via a crafted certificate.

## References
- http://www.debian.org/security/2017/dsa-3866
- http://www.securityfocus.com/bid/98756
- http://www.ubuntu.com/usn/USN-3301-1
- https://www.strongswan.org/blog/2017/05/30/strongswan-vulnerability-%28cve-2017-9023%29.html
