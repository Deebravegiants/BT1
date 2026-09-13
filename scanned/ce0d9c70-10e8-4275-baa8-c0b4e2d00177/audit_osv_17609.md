# [M] CVE-2020-17482

## Summary
Severity: Medium
Advisory: CVE-2020-17482
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-10-02
Source: https://osv.dev/vulnerability/CVE-2020-17482
Type: osv

## Details
An issue has been found in PowerDNS Authoritative Server before 4.3.1 where an authorized user with the ability to insert crafted records into a zone might be able to leak the content of uninitialized memory.

## References
- https://doc.powerdns.com/authoritative/security-advisories/powerdns-advisory-2020-05.html
- https://github.com/PowerDNS/pdns
- https://security.gentoo.org/glsa/202012-18
