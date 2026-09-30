# [H] Openimageio: heap-buffer-overflow in file src/gif.imageio/gifinput.cpp

## Summary
Severity: High
Advisory: CVE-2023-3430
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-18
Source: https://osv.dev/vulnerability/CVE-2023-3430
Type: osv

## Details
A vulnerability was found in OpenImageIO, where a heap buffer overflow exists in the src/gif.imageio/gifinput.cpp file. This flaw allows a remote attacker to pass a specially crafted file to the application, which triggers a heap-based buffer overflow and could cause a crash, leading to a denial of service.

## References
- https://packages.fedoraproject.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/3xxx/CVE-2023-3430.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-3430
- https://bugzilla.redhat.com/show_bug.cgi?id=2218380
- https://github.com/AcademySoftwareFoundation/OpenImageIO/issues/3840
