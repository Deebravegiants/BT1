# [C] Net::Dropbear versions before 0.14 for Perl contains a vulnerable version of libtomcrypt

## Summary
Severity: Critical
Advisory: CVE-2025-15638
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2025-15638
Type: osv

## Details
Net::Dropbear versions before 0.14 for Perl contains a vulnerable version of libtomcrypt.

Net::Dropbear versions before 0.14 includes versions of Dropbear 2019.78 or earlier. These include versions of libtomcrypt v1.18.1 or earlier, which is affected by CVE-2016-6129 and CVE-2018-12437.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15638.json
- https://metacpan.org/release/ATRODO/Net-Dropbear-0.14/source/dropbear/libtomcrypt/changes
- https://nvd.nist.gov/vuln/detail/CVE-2025-15638
- https://www.cve.org/CVERecord?id=CVE-2016-6129
- https://www.cve.org/CVERecord?id=CVE-2018-12437
- https://github.com/atrodo/Net-Dropbear
