# [M] Kernel: deadlock leading to denial of service in tipc_crypto_key_revoke

## Summary
Severity: Medium
Advisory: CVE-2024-0641
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-17
Source: https://osv.dev/vulnerability/CVE-2024-0641
Type: osv

## Details
A denial of service vulnerability was found in tipc_crypto_key_revoke in net/tipc/crypto.c in the Linux kernel’s TIPC subsystem. This flaw allows guests with local user privileges to trigger a deadlock and potentially crash the system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.kernel.org/pub/scm/linux/kernel
- https://access.redhat.com/security/cve/CVE-2024-0641
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0641.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0641
- https://bugzilla.redhat.com/show_bug.cgi?id=2258757
- https://github.com/torvalds/linux/commit/08e50cf071847323414df0835109b6f3560d44f5
