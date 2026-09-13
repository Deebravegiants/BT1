# [H] DBI versions before 1.648 for Perl saved errors in a limited-sized buffer

## Summary
Severity: High
Advisory: CVE-2026-9698
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-9698
Type: osv

## Details
DBI versions before 1.648 for Perl saved errors in a limited-sized buffer.

Error messages that were returned when RaiseError, PrintError or HandleError were set were written to a 200-byte buffer without a length limit.

Attackers that can influence the error text in an application can trigger a buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2026/06/09/9
- https://cpan.org/modules
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-9698.json
- https://access.redhat.com/errata/RHSA-2026:38512
- https://access.redhat.com/errata/RHSA-2026:38513
- https://access.redhat.com/errata/RHSA-2026:38901
- https://access.redhat.com/errata/RHSA-2026:53371
- https://access.redhat.com/errata/RHSA-2026:62667
- https://access.redhat.com/security/cve/CVE-2026-9698
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/9xxx/CVE-2026-9698.json
- https://metacpan.org/release/HMBRAND/DBI-1.648/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-9698
- https://bugzilla.redhat.com/show_bug.cgi?id=2486734
- https://github.com/perl5-dbi/dbi/commit/bfe5d73c162d2d1f761a639a0aa33aad6a9eb54e.patch
- https://github.com/perl5-dbi/dbi
