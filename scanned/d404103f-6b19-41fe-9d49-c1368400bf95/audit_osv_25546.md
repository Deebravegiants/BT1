# [M] Openjpeg: resource exhaustion will occur in the opj_t1_decode_cblks function in the tcd.c

## Summary
Severity: Medium
Advisory: CVE-2023-39329
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-07-13
Source: https://osv.dev/vulnerability/CVE-2023-39329
Type: osv

## Details
A flaw was found in OpenJPEG. A resource exhaustion can occur in the opj_t1_decode_cblks function in tcd.c through a crafted image file, causing a denial of service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://catalog.redhat.com/software/containers/
- https://www.openjpeg.org/
- https://access.redhat.com/errata/RHSA-2026:4128
- https://access.redhat.com/security/cve/CVE-2023-39329
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39329.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-39329
- https://bugzilla.redhat.com/show_bug.cgi?id=2295816
