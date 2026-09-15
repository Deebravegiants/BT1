# [H] Handcrafted repo metadata may cause arbitrary local files to be overwritten by libzypp

## Summary
Severity: High
Advisory: CVE-2026-25707
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-29
Source: https://osv.dev/vulnerability/CVE-2026-25707
Type: osv

## Details
A relative path traversal bug problem when processing repository metadata in libzypp before 17.38.10 could be used by remote attackers supplying repositories to overwrite files on the system, leading to denial of service or privilege escalation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25707.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25707
- https://bugzilla.suse.com/show_bug.cgi?id=1259802
- https://github.com/openSUSE/libzypp/commit/f09feda7fca03c941218aab0bb161cc82b185b6b
- https://github.com/openSUSE/libzypp
