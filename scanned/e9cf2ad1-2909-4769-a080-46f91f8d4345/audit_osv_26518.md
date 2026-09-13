# [M] media: hi846: Fix memleak in hi846_init_controls()

## Summary
Severity: Medium
Advisory: CVE-2023-53300
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53300
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <6.1.28, >=6.2.0 <6.2.15, >=6.3.0 <6.3.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: hi846: Fix memleak in hi846_init_controls()

hi846_init_controls doesn't clean the allocated ctrl_hdlr
in case there is a failure, which causes memleak. Add
v4l2_ctrl_handler_free to free the resource properly.

## References
- https://git.kernel.org/stable/c/07f0f15e5db60c5b0722049d3251ef4a46dc3b76
- https://git.kernel.org/stable/c/12a80b1490e398f5ad7157508cf32b73511de5fc
- https://git.kernel.org/stable/c/2649c1a20e8e399ee955d0e22192f9992662c3d2
- https://git.kernel.org/stable/c/fd22e8c8c38fb40f130d3a60e52c59996a5bbae9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53300.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53300
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
