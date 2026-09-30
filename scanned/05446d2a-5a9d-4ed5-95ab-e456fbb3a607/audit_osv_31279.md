# [H] Libnbd: nbd server improper certificate validation

## Summary
Severity: High
Advisory: CVE-2024-7383
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-08-05
Source: https://osv.dev/vulnerability/CVE-2024-7383
Type: osv

## Details
A flaw was found in libnbd. The client did not always correctly verify the NBD server's certificate when using TLS to connect to an NBD server. This issue allows a man-in-the-middle attack on NBD traffic.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.libguestfs.org/archives/list/guestfs@lists.libguestfs.org/message/LHR3BW6RJ7K4BJBQIYV3GTZLSY27VZO2
- https://lists.libguestfs.org/archives/list/guestfs@lists.libguestfs.org/thread/ENZY4LHLARA3N4C3JUNLPYUCXHFO7BWQ/
- https://access.redhat.com/errata/RHSA-2024:6757
- https://access.redhat.com/errata/RHSA-2024:6964
- https://access.redhat.com/security/cve/CVE-2024-7383
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7383.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7383
- https://bugzilla.redhat.com/show_bug.cgi?id=2302865
- https://gitlab.com/nbdkit/libnbd
