# [M] File-roller: file-roller: stack buffer overflow in parse_progress_line for 7z and rar handlers

## Summary
Severity: Medium
Advisory: CVE-2026-78322
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-78322
Type: osv

## Details
A flaw was found in file-roller. When opening or extracting a malicious 7z or RAR archive containing a file entry with an excessively long path, file-roller's progress-line parsing copies the path into a fixed-size stack buffer using an unbounded string copy. This can trigger a stack buffer overflow and cause file-roller to terminate, resulting in a denial of service. To exploit this flaw, a victim must open or extract the crafted archive using file-roller.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-78322
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/78xxx/CVE-2026-78322.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-78322
- https://bugzilla.redhat.com/show_bug.cgi?id=2521767
- https://gitlab.gnome.org/GNOME/file-roller/-/issues/327
- https://gitlab.gnome.org/GNOME/file-roller/-/commit/ffb76dc866342cef6a4914873faaa880d14d5aa4
