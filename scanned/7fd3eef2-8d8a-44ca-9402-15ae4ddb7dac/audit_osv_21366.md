# [H] CVE-2021-42522

## Summary
Severity: High
Advisory: CVE-2021-42522
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-25
Source: https://osv.dev/vulnerability/CVE-2021-42522
Type: osv

## Details
There is a Information Disclosure vulnerability in anjuta/plugins/document-manager/anjuta-bookmarks.c. This issue was caused by the incorrect use of libxml2 API. The vendor forgot to call 'g_free()' to release the return value of 'xmlGetProp()'.

## References
- https://gitlab.gnome.org/GNOME/anjuta/-/issues/12
