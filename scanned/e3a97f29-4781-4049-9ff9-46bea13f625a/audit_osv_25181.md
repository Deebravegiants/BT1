# [M] Heap-buffer-overflow in extractimagesection()

## Summary
Severity: Medium
Advisory: CVE-2023-3164
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-11-02
Source: https://osv.dev/vulnerability/CVE-2023-3164
Type: osv

## Details
A heap-buffer-overflow vulnerability was found in LibTIFF, in extractImageSection() at tools/tiffcrop.c:7916 and tools/tiffcrop.c:7801. This flaw allows attackers to cause a denial of service via a crafted tiff file.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-3164
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3164.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3164
- https://bugzilla.redhat.com/show_bug.cgi?id=2213531
- https://gitlab.com/libtiff/libtiff/-/issues/542
