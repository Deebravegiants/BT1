# [M] CVE-2023-6176

## Summary
Severity: Medium
Advisory: CVE-2023-6176
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-16
Source: https://osv.dev/vulnerability/CVE-2023-6176
Type: osv

## Details
A null pointer dereference flaw was found in the Linux kernel API for the cryptographic algorithm scatterwalk functionality. This issue occurs when a user constructs a malicious packet with specific socket configuration, which could allow a local user to crash the system or escalate their privileges on the system.

## References
- http://packetstormsecurity.com/files/177029/Kernel-Live-Patch-Security-Notice-LSN-0100-1.html
- https://access.redhat.com/errata/RHSA-2024:2950
- https://access.redhat.com/errata/RHSA-2024:3138
- https://access.redhat.com/security/cve/CVE-2023-6176
- https://access.redhat.com/errata/RHSA-2024:2394
- https://bugzilla.redhat.com/show_bug.cgi?id=2219359
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cfaa80c91f6f99b9342b6557f0f0e1143e434066
