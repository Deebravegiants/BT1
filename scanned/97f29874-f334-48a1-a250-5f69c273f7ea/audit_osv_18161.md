# [H] CVE-2020-24696

## Summary
Severity: High
Advisory: CVE-2020-24696
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-24696
Type: osv

## Details
An issue was discovered in PowerDNS Authoritative through 4.3.0 when --enable-experimental-gss-tsig is used. A remote, unauthenticated attacker can trigger a race condition leading to a crash, or possibly arbitrary code execution, by sending crafted queries with a GSS-TSIG signature.

## References
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2020-06.html
