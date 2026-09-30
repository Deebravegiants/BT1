# [H] Libtiff: null pointer dereference in tif_dirinfo.c

## Summary
Severity: High
Advisory: CVE-2024-7006
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-08-08
Source: https://osv.dev/vulnerability/CVE-2024-7006
Type: osv

## Details
A null pointer dereference flaw was found in Libtiff via `tif_dirinfo.c`. This issue may allow an attacker to trigger memory allocation failures through certain means, such as restricting the heap space size or injecting faults, causing a segmentation fault. This can cause an application crash, eventually leading to a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/01/msg00019.html
- https://access.redhat.com/errata/RHSA-2024:6360
- https://access.redhat.com/errata/RHSA-2024:8833
- https://access.redhat.com/errata/RHSA-2024:8914
- https://access.redhat.com/security/cve/CVE-2024-7006
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7006.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7006
- https://security.netapp.com/advisory/ntap-20240920-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2302996
- https://gitlab.com/libtiff/libtiff
