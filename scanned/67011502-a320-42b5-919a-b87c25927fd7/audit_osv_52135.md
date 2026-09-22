# [H] CVE-2021-47111

## Summary
Severity: High
Advisory: CVE-2021-47111
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-03-15
Source: https://osv.dev/vulnerability/CVE-2021-47111
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

xen-netback: take a reference to the RX task thread

Do this in order to prevent the task from being freed if the thread
returns (which can be triggered by the frontend) before the call to
kthread_stop done as part of the backend tear down. Not taking the
reference will lead to a use-after-free in that scenario. Such
reference was taken before but dropped as part of the rework done in
2ac061ce97f4.

Reintroduce the reference taking and add a comment this time
explaining why it's needed.

This is XSA-374 / CVE-2021-28691.

## References
- https://git.kernel.org/stable/c/107866a8eb0b664675a260f1ba0655010fac1e08
- https://git.kernel.org/stable/c/6b53db8c4c14b4e7256f058d202908b54a7b85b4
- https://git.kernel.org/stable/c/caec9bcaeb1a5f03f2d406305355c853af10c13e
