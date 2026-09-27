# [H] CVE-2024-52530

## Summary
Severity: High
Advisory: CVE-2024-52530
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-11-11
Source: https://osv.dev/vulnerability/CVE-2024-52530
Type: osv

## Details
GNOME libsoup before 3.6.0 allows HTTP request smuggling in some configurations because '\0' characters at the end of header names are ignored, i.e., a "Transfer-Encoding\0: chunked" header is treated the same as a "Transfer-Encoding: chunked" header.

## References
- https://gitlab.gnome.org/Teams/Releng/security/-/wikis/home
- https://lists.debian.org/debian-lts-announce/2024/12/msg00014.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52530.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52530
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/377
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/402
