# [M] Qemu-kvm: net: assertion failure in update_sctp_checksum()

## Summary
Severity: Medium
Advisory: CVE-2024-3567
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2024-3567
Type: osv

## Details
A flaw was found in QEMU. An assertion failure was present in the update_sctp_checksum() function in hw/net/net_tx_pkt.c when trying to calculate the checksum of a short-sized fragmented packet. This flaw allows a malicious guest to crash QEMU and cause a denial of service condition.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/errata/RHSA-2025:4492
- https://access.redhat.com/security/cve/CVE-2024-3567
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3567.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3567
- https://security.netapp.com/advisory/ntap-20240822-0007/
- https://bugzilla.redhat.com/show_bug.cgi?id=2274339
- https://gitlab.com/qemu-project/qemu/-/issues/2273
- https://gitlab.com/qemu-project/qemu/
