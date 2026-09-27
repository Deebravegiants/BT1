# [H] Archive::Tar versions before 3.08 for Perl extract hardlinks to attacker controlled paths outside the extraction directory

## Summary
Severity: High
Advisory: CVE-2026-42497
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-42497
Type: osv

## Details
Archive::Tar versions before 3.08 for Perl extract hardlinks to attacker controlled paths outside the extraction directory.

_make_special_file() passes the tar header's linkname to link() without validating it against absolute paths or .. segments, creating a hardlink that shares the victim file's inode.

A subsequent write through the extracted name modifies the victim file, and the post-extraction chmod, chown, and utime block in _extract_file() (guarded only against symlinks via -l) applies the tar header's mode, owner, and timestamps to the shared inode during extraction alone.

## References
- https://cpan.org/modules
- https://www.cve.org/CVERecord?id=CVE-2026-42496
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42497.json
- https://metacpan.org/release/BINGOS/Archive-Tar-3.08/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-42497
- https://github.com/jib/archive-tar-new/commit/17c873492a05eddc0de18c1485e0b2cccd5a9158.patch
- https://github.com/jib/archive-tar-new
