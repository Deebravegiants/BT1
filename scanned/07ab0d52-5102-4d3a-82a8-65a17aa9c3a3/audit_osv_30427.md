# [M] CVE-2024-52531

## Summary
Severity: Medium
Advisory: CVE-2024-52531
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2024-11-11
Source: https://osv.dev/vulnerability/CVE-2024-52531
Type: osv

## Details
GNOME libsoup before 3.6.1 allows a buffer overflow in applications that perform conversion to UTF-8 in soup_header_parse_param_list_strict. There is a plausible way to reach this remotely via soup_message_headers_get_content_type (e.g., an application may want to retrieve the content type of a request or response).

## References
- https://gitlab.gnome.org/Teams/Releng/security/-/wikis/home
- https://lists.debian.org/debian-lts-announce/2024/12/msg00014.html
- https://offsec.almond.consulting/using-aflplusplus-on-bug-bounty-programs-an-example-with-gnome-libsoup.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52531.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-52531
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/407
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/407#note_2316401
