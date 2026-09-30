# [M] CVE-2023-4134

## Summary
Severity: Medium
Advisory: CVE-2023-4134
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2023-4134
Type: osv

## Details
A use-after-free vulnerability was found in the cyttsp4_core driver in the Linux kernel. This issue occurs in the device cleanup routine due to a possible rearming of the watchdog_timer from the workqueue. This could allow a local user to crash the system, causing a denial of service.

## References
- https://access.redhat.com/security/cve/CVE-2023-4134
- https://bugzilla.redhat.com/show_bug.cgi?id=2221700
