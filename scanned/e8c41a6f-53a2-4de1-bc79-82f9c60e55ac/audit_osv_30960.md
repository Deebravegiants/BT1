# [M] Openjpeg: heap buffer overflow in bin/common/color.c

## Summary
Severity: Medium
Advisory: CVE-2024-56826
CVSS: 5.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:H)
Published: 2025-01-09
Source: https://osv.dev/vulnerability/CVE-2024-56826
Type: osv

## Details
A flaw was found in the OpenJPEG project. A heap buffer overflow condition may be triggered when certain options are specified while using the opj_decompress utility.  This can lead to an application crash or other undefined behavior.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2025/04/msg00002.html
- https://access.redhat.com/errata/RHSA-2025:7309
- https://access.redhat.com/security/cve/CVE-2024-56826
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56826.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56826
- https://bugzilla.redhat.com/show_bug.cgi?id=2335172
- https://github.com/uclouvain/openjpeg/issues/1563
- https://github.com/uclouvain/openjpeg/commit/e492644fbded4c820ca55b5e50e598d346e850e8
- https://github.com/uclouvain/openjpeg
