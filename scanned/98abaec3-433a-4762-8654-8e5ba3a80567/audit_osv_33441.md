# [C] BSON::XS versions 0.8.4 and earlier for Perl includes a bundled libbson 1.1.7, which has several vulnerabilities

## Summary
Severity: Critical
Advisory: CVE-2025-40906
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-16
Source: https://osv.dev/vulnerability/CVE-2025-40906
Type: osv

## Details
BSON::XS versions 0.8.4 and earlier for Perl includes a bundled libbson 1.1.7, which has several vulnerabilities.

Those include CVE-2017-14227, CVE-2018-16790, CVE-2023-0437, CVE-2024-6381, CVE-2024-6383, and CVE-2025-0755. 

BSON-XS was the official Perl XS implementation of MongoDB's BSON serialization, but this distribution has reached its end of life as of August 13, 2020 and is no longer supported.

## References
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40906.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40906
- https://www.mongodb.com/community/forums/t/mongodb-perl-driver-end-of-life/7890
- https://github.com/mongodb-labs/mongo-perl-bson-xs
- https://lists.debian.org/debian-lts-announce/2025/05/msg00012.html
