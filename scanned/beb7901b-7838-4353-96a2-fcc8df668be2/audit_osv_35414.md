# [H] Gdk‑pixbuf: heap‑buffer‑overflow in gdk‑pixbuf

## Summary
Severity: High
Advisory: CVE-2025-7345
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-08
Source: https://osv.dev/vulnerability/CVE-2025-7345
Type: osv

## Details
A flaw exists in gdk‑pixbuf within the gdk_pixbuf__jpeg_image_load_increment function (io-jpeg.c) and in glib’s g_base64_encode_step (glib/gbase64.c). When processing maliciously crafted JPEG images, a heap buffer overflow can occur during Base64 encoding, allowing out-of-bounds reads from heap memory, potentially causing application crashes or arbitrary code execution.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://gitlab.gnome.org/GNOME/
- https://lists.debian.org/debian-lts-announce/2025/10/msg00024.html
- https://access.redhat.com/errata/RHSA-2025:12841
- https://access.redhat.com/errata/RHSA-2025:12862
- https://access.redhat.com/errata/RHSA-2025:13315
- https://access.redhat.com/errata/RHSA-2025:14574
- https://access.redhat.com/errata/RHSA-2025:14575
- https://access.redhat.com/errata/RHSA-2025:14576
- https://access.redhat.com/errata/RHSA-2025:14585
- https://access.redhat.com/errata/RHSA-2025:14618
- https://access.redhat.com/errata/RHSA-2025:14646
- https://access.redhat.com/errata/RHSA-2025:14647
- https://access.redhat.com/errata/RHSA-2025:14683
- https://access.redhat.com/security/cve/CVE-2025-7345
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/7xxx/CVE-2025-7345.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-7345
- https://bugzilla.redhat.com/show_bug.cgi?id=2377063
- https://gitlab.gnome.org/GNOME/gdk-pixbuf/-/issues/249
