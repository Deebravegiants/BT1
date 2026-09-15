# [M] Libnbd: crash or misbehaviour when nbd server returns an unexpected block size

## Summary
Severity: Medium
Advisory: CVE-2023-5215
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-28
Source: https://osv.dev/vulnerability/CVE-2023-5215
Type: osv

## Details
A flaw was found in libnbd. A server can reply with a block size larger than 2^63 (the NBD spec states the size is a 64-bit unsigned value). This issue could lead to an application crash or other unintended behavior for NBD clients that doesn't treat the return value of the nbd_get_size() function correctly.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://listman.redhat.com/archives/libguestfs/2023-September/032635.html
- https://access.redhat.com/errata/RHSA-2024:2204
- https://access.redhat.com/security/cve/CVE-2023-5215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5215.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5215
- https://bugzilla.redhat.com/show_bug.cgi?id=2241041
