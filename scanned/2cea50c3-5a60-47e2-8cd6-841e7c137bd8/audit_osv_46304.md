# [M] drm/amd/display: Fix null pointer dereference in error message

## Summary
Severity: Medium
Advisory: CVE-2023-52862
Ecosystem: Linux
CVSS: 4.1 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52862
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.5.0 <6.5.12, >=6.6.0 <6.6.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix null pointer dereference in error message

This patch fixes a null pointer dereference in the error message that is
printed when the Display Core (DC) fails to initialize. The original
message includes the DC version number, which is undefined if the DC is
not initialized.

## References
- https://git.kernel.org/stable/c/0c3601a2fbfb265ce283651480e30c8e60459112
- https://git.kernel.org/stable/c/8b72c5d4a5d25e76b16283397c40b8b3c0d70019
- https://git.kernel.org/stable/c/97ef07182ac46b069bb5e7d46cb903a764d67898
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52862.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52862
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
