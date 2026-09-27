# [H] CVE-2022-48622

## Summary
Severity: High
Advisory: CVE-2022-48622
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-26
Source: https://osv.dev/vulnerability/CVE-2022-48622
Type: osv

## Details
In GNOME GdkPixbuf (aka gdk-pixbuf) through 2.42.10, the ANI (Windows animated cursor) decoder encounters heap memory corruption (in ani_load_chunk in io-ani.c) when parsing chunks in a crafted .ani file. A crafted file could allow an attacker to overwrite heap metadata, leading to a denial of service or code execution attack. This occurs in gdk_pixbuf_set_option() in gdk-pixbuf.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48622.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48622
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/202
