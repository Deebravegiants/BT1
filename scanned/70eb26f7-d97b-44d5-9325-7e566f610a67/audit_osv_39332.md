# [M] Net::CIDR::Lite versions before 0.24 for Perl does not properly consider extraneous zero characters in CIDR mask values, which may allow IP ACL bypass

## Summary
Severity: Medium
Advisory: CVE-2026-45191
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/CVE-2026-45191
Type: osv

## Details
Net::CIDR::Lite versions before 0.24 for Perl does not properly consider extraneous zero characters in CIDR mask values, which may allow IP ACL bypass.

Mask forms like "/00" and "/01" pass validation and parse to the same prefix as their unpadded value.

See also CVE-2026-45190.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-45190
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45191.json
- https://metacpan.org/release/STIGTSP/Net-CIDR-Lite-0.24/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-45191
- https://github.com/stigtsp/Net-CIDR-Lite/commit/24e2c439ec405e5256024b9acefd4f7008c5ed0c.patch
- https://github.com/stigtsp/Net-CIDR-Lite
