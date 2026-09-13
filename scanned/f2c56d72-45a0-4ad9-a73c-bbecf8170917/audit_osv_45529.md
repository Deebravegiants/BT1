# [M] GNOME libsoup before 3.6.1 allows a buffer overflow in applications that perform conversion to...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1278
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/JLSEC-2026-1278
Type: osv

## Affected
- Julia: `Soup3_jll` — affected unspecified

## Details
GNOME libsoup before 3.6.1 allows a buffer overflow in applications that perform conversion to UTF-8 in `soup_header_parse_param_list_strict`. There is a plausible way to reach this remotely via `soup_message_headers_get_content_type` (e.g., an application may want to retrieve the content type of a request or response).

## References
- https://github.com/advisories/GHSA-5mc3-gwcr-mgc3
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/407
- https://gitlab.gnome.org/GNOME/libsoup/-/merge_requests/407#note_2316401
- https://gitlab.gnome.org/Teams/Releng/security/-/wikis/home
- https://lists.debian.org/debian-lts-announce/2024/12/msg00014.html
- https://nvd.nist.gov/vuln/detail/CVE-2024-52531
- https://offsec.almond.consulting/using-aflplusplus-on-bug-bounty-programs-an-example-with-gnome-libsoup.html
