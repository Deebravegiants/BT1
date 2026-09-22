# [H] CVE-2020-2025

## Summary
Severity: High
Advisory: CVE-2020-2025
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2020-05-19
Source: https://osv.dev/vulnerability/CVE-2020-2025
Type: osv

## Details
Kata Containers before 1.11.0 on Cloud Hypervisor persists guest filesystem changes to the underlying image file on the host. A malicious guest can overwrite the image file to gain control of all subsequent guest VMs. Since Kata Containers uses the same VM image file with all VMMs, this issue may also affect QEMU and Firecracker based guests.

## References
- https://github.com/kata-containers/runtime/pull/2487
