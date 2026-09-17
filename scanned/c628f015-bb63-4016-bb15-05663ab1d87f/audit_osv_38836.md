# [C] Archive::Tar versions before 3.08 for Perl extract symlinks with attacker controlled targets outside the extraction directory

## Summary
Severity: Critical
Advisory: CVE-2026-42496
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-42496
Type: osv

## Details
Archive::Tar versions before 3.08 for Perl extract symlinks with attacker controlled targets outside the extraction directory.

_make_special_file() passes the tar header's linkname to symlink() without validating it against absolute paths or .. segments. The secure-extract mode check that guards regular file extraction does not cover the symlink target.

A subsequent open through the extracted name reads or writes the attacker chosen path.

## References
- https://cpan.org/modules
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-42496.json
- https://www.cve.org/CVERecord?id=CVE-2026-42497
- https://access.redhat.com/errata/RHSA-2026:30851
- https://access.redhat.com/errata/RHSA-2026:30852
- https://access.redhat.com/errata/RHSA-2026:30856
- https://access.redhat.com/errata/RHSA-2026:30857
- https://access.redhat.com/security/cve/CVE-2026-42496
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42496.json
- https://metacpan.org/release/BINGOS/Archive-Tar-3.08/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-42496
- https://bugzilla.redhat.com/show_bug.cgi?id=2481314
- https://github.com/jib/archive-tar-new/commit/17c873492a05eddc0de18c1485e0b2cccd5a9158.patch
- https://github.com/jib/archive-tar-new
