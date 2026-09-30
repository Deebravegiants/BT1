# [M] Kernel: potential deadlock on &net->sctp.addr_wq_lock leading to dos

## Summary
Severity: Medium
Advisory: CVE-2024-0639
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-17
Source: https://osv.dev/vulnerability/CVE-2024-0639
Type: osv

## Details
A denial of service vulnerability due to a deadlock was found in sctp_auto_asconf_init in net/sctp/socket.c in the Linux kernel’s SCTP subsystem. This flaw allows guests with local user privileges to trigger a deadlock and potentially crash the system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://git.kernel.org/pub/scm/linux/kernel
- https://access.redhat.com/errata/RHSA-2023:6583
- https://access.redhat.com/security/cve/CVE-2024-0639
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/0xxx/CVE-2024-0639.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-0639
- https://bugzilla.redhat.com/show_bug.cgi?id=2258754
- https://github.com/torvalds/linux/commit/6feb37b3b06e9049e20dcf7e23998f92c9c5be9a
