# [H] IO::Compress versions before 2.220 for Perl can execute arbitrary code in File::GlobMapper via an attacker-controlled output glob

## Summary
Severity: High
Advisory: CVE-2026-48962
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-48962
Type: osv

## Details
IO::Compress versions before 2.220 for Perl can execute arbitrary code in File::GlobMapper via an attacker-controlled output glob.

_parseOutputGlob() wraps the caller-supplied output glob string in double quotes and stores it in the parser state; _getFiles() then runs the stored expression through eval STRING. A literal double quote in the output glob closes the dquote wrapper, and the characters that follow are evaluated as Perl.

Arbitrary Perl in the output glob executes at the calling process's privilege.

## References
- http://www.openwall.com/lists/oss-security/2026/05/27/4
- https://cpan.org/modules
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-48962.json
- https://access.redhat.com/errata/RHSA-2026:29182
- https://access.redhat.com/errata/RHSA-2026:29210
- https://access.redhat.com/errata/RHSA-2026:29867
- https://access.redhat.com/errata/RHSA-2026:29941
- https://access.redhat.com/errata/RHSA-2026:30085
- https://access.redhat.com/errata/RHSA-2026:30086
- https://access.redhat.com/errata/RHSA-2026:30115
- https://access.redhat.com/errata/RHSA-2026:30843
- https://access.redhat.com/errata/RHSA-2026:30851
- https://access.redhat.com/errata/RHSA-2026:30858
- https://access.redhat.com/errata/RHSA-2026:30859
- https://access.redhat.com/errata/RHSA-2026:30860
- https://access.redhat.com/errata/RHSA-2026:50262
- https://access.redhat.com/security/cve/CVE-2026-48962
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48962.json
- https://metacpan.org/release/PMQS/IO-Compress-2.220/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-48962
