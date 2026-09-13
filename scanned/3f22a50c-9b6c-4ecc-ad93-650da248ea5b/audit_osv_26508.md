# [M] media: bdisp: Add missing check for create_workqueue

## Summary
Severity: Medium
Advisory: CVE-2023-53289
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53289
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.14.315, >=4.15.0 <4.19.283, >=4.20.0 <5.4.243, >=5.5.0 <5.10.180, >=5.11.0 <5.15.111, >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: bdisp: Add missing check for create_workqueue

Add the check for the return value of the create_workqueue
in order to avoid NULL pointer dereference.

## References
- https://git.kernel.org/stable/c/0d09ce05724cfb3f5c5136893bec95305c641875
- https://git.kernel.org/stable/c/2371adeab717d8fe32144a84f3491a03c5838cfb
- https://git.kernel.org/stable/c/2bfbe3ad371ac5349302833198df14e442622cbc
- https://git.kernel.org/stable/c/4362444dca02ab44ac844feda3cf6238ef953673
- https://git.kernel.org/stable/c/519b0849401194745ea40f9e07513b870afc1b42
- https://git.kernel.org/stable/c/c2e55481731b0e8c96f30f661e430aa884fbd354
- https://git.kernel.org/stable/c/c6a315f0b14074ac89723f55b749a557dda0ae2b
- https://git.kernel.org/stable/c/eef95a2745cb91559bb03aa111c228fe38deaf64
- https://git.kernel.org/stable/c/fc1aeafdf6fb0a136c2257000f0d478ee62953fe
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53289.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53289
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
