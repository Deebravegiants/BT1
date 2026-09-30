# [M] Libnbd: malicious nbd server may crash libnbd

## Summary
Severity: Medium
Advisory: CVE-2023-5871
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-11-27
Source: https://osv.dev/vulnerability/CVE-2023-5871
Type: osv

## Details
A flaw was found in libnbd, due to a malicious Network Block Device (NBD), a protocol for accessing Block Devices such as hard disks over a Network. This issue may allow a malicious NBD server to cause a Denial of Service.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.libguestfs.org/archives/list/guestfs@lists.libguestfs.org/thread/PFVUCMPFQUDC23JXSCUUPXIGDZ7XCFMD/
- https://access.redhat.com/errata/RHSA-2024:2204
- https://access.redhat.com/security/cve/CVE-2023-5871
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/5xxx/CVE-2023-5871.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-5871
- https://bugzilla.redhat.com/show_bug.cgi?id=2247308
