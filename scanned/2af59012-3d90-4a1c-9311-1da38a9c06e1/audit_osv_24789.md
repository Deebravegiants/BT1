# [H] Dma reentrancy issue (incomplete fix for cve-2021-3750)

## Summary
Severity: High
Advisory: CVE-2023-2680
CVSS: 7.5 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CVE-2023-2680
Type: osv

## Details
This CVE exists because of an incomplete fix for CVE-2021-3750. More specifically, the qemu-kvm package as released for Red Hat Enterprise Linux 9.1 via RHSA-2022:7967 included a version of qemu-kvm that was actually missing the fix for CVE-2021-3750.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://packages.fedoraproject.org/
- https://access.redhat.com/security/cve/CVE-2023-2680
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2680.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2680
- https://security.netapp.com/advisory/ntap-20231116-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=2203387
