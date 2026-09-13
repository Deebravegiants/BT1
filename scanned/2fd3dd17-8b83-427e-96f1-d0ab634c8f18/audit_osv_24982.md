# [M] Libtiff: null pointer dereference in tif_dir.c

## Summary
Severity: Medium
Advisory: CVE-2023-2908
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-06-30
Source: https://osv.dev/vulnerability/CVE-2023-2908
Type: osv

## Details
A null pointer dereference issue was found in Libtiff's tif_dir.c file. This issue may allow an attacker to pass a crafted TIFF image file to the tiffcp utility which triggers a runtime error that causes undefined behavior. This will result in an application crash, eventually leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/security/cve/CVE-2023-2908
- https://lists.debian.org/debian-lts-announce/2023/07/msg00034.html
- https://lists.debian.org/debian-lts-announce/2025/01/msg00019.html
- https://packages.fedoraproject.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2908.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2908
- https://security.netapp.com/advisory/ntap-20230731-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2218830
- https://gitlab.com/libtiff/libtiff/-/commit/9bd48f0dbd64fb94dc2b5b05238fde0bfdd4ff3f
- https://gitlab.com/libtiff/libtiff/-/merge_requests/479
