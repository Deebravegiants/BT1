# [M] Libsoup: off-by-one out-of-bounds read in find_boundary() in soup-multipart.c

## Summary
Severity: Medium
Advisory: CVE-2025-4969
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2025-05-21
Source: https://osv.dev/vulnerability/CVE-2025-4969
Type: osv

## Details
A vulnerability was found in the libsoup package. This flaw stems from its failure to correctly verify the termination of multipart HTTP messages. This can allow a remote attacker to send a specially crafted multipart HTTP body, causing the libsoup-consuming server to read beyond its allocated memory boundaries (out-of-bounds read).

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2025-4969
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/4xxx/CVE-2025-4969.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-4969
- https://bugzilla.redhat.com/show_bug.cgi?id=2367552
- https://gitlab.gnome.org/GNOME/libsoup/-/issues/447
- https://gitlab.gnome.org/GNOME/libsoup
