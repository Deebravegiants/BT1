# [M] can: j1939: j1939_send_one(): fix missing CAN header initialization

## Summary
Severity: Medium
Advisory: CVE-2022-49845
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49845
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.225, >=5.5.0 <5.10.155, >=5.11.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: j1939: j1939_send_one(): fix missing CAN header initialization

The read access to struct canxl_frame::len inside of a j1939 created
skbuff revealed a missing initialization of reserved and later filled
elements in struct can_frame.

This patch initializes the 8 byte CAN header with zero.

## References
- https://git.kernel.org/stable/c/2719f82ad5d8199cf5f346ea8bb3998ad5323b72
- https://git.kernel.org/stable/c/3eb3d283e8579a22b81dd2ac3987b77465b2a22f
- https://git.kernel.org/stable/c/69e86c6268d59ceddd0abe9ae8f1f5296f316c3c
- https://git.kernel.org/stable/c/d0513b095e1ef1469718564dec3fb3348556d0a8
- https://git.kernel.org/stable/c/f8e0edeaa0f2b860bdbbf0aafb4492533043d650
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49845.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
