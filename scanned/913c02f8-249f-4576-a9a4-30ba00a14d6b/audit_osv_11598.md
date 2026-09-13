# [H] CVE-2017-9022

## Summary
Severity: High
Advisory: CVE-2017-9022
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-08
Source: https://osv.dev/vulnerability/CVE-2017-9022
Type: osv

## Details
The gmp plugin in strongSwan before 5.5.3 does not properly validate RSA public keys before calling mpz_powm_sec, which allows remote peers to cause a denial of service (floating point exception and process crash) via a crafted certificate.

## References
- http://www.debian.org/security/2017/dsa-3866
- http://www.securityfocus.com/bid/98760
- http://www.ubuntu.com/usn/USN-3301-1
- https://www.strongswan.org/blog/2017/05/30/strongswan-vulnerability-%28cve-2017-9022%29.html
