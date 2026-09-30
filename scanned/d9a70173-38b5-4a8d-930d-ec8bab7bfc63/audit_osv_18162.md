# [H] CVE-2020-24697

## Summary
Severity: High
Advisory: CVE-2020-24697
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-24697
Type: osv

## Details
An issue was discovered in PowerDNS Authoritative through 4.3.0 when --enable-experimental-gss-tsig is used. A remote, unauthenticated attacker can cause a denial of service by sending crafted queries with a GSS-TSIG signature.

## References
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2020-06.html
