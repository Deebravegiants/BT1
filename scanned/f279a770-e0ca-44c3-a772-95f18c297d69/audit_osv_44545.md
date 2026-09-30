# [M] Gvfs: mtp: out-of-bounds read in do_read()

## Summary
Severity: Medium
Advisory: CVE-2026-84270
CVSS: 4.3 (CVSS:3.1/AV:P/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-84270
Type: osv

## Details
A flaw was found in the MTP backend in gvfs. When reading a file from a mounted MTP device, do_read() in gvfsbackendmtp.c trusts the data length returned by the device without limiting it to the original size requested by the client. If a malicious MTP device responds with more bytes than requested, this unrestricted length is passed directly to memcpy(). This causes the operation to read memory outside the intended boundaries. This allows an attacker who plugs in a malicious MTP device to cause a segmentation fault when a file is read and crash the gvfsd-mtp process, resulting in a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2026-84270
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84270.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-84270
- https://bugzilla.redhat.com/show_bug.cgi?id=2526794
- https://gitlab.gnome.org/GNOME/gvfs/-/issues/864
- https://gitlab.gnome.org/GNOME/gvfs
