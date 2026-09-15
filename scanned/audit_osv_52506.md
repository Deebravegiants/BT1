# [H] CVE-2021-47521

## Summary
Severity: High
Advisory: CVE-2021-47521
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-24
Source: https://osv.dev/vulnerability/CVE-2021-47521
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: sja1000: fix use after free in ems_pcmcia_add_card()

If the last channel is not available then "dev" is freed.  Fortunately,
we can just use "pdev->irq" instead.

Also we should check if at least one channel was set up.

## References
- https://git.kernel.org/stable/c/ccf070183e4655824936c0f96c4a2bcca93419aa
- https://git.kernel.org/stable/c/1a295fea90e1acbe80c6d4940f5ff856edcd6bec
- https://git.kernel.org/stable/c/1dd5b819f7e406dc15bbc7670596ff25261aaa2a
- https://git.kernel.org/stable/c/3ec6ca6b1a8e64389f0212b5a1b0f6fed1909e45
- https://git.kernel.org/stable/c/474f9a8534f5f89841240a7e978bafd6e1e039ce
- https://git.kernel.org/stable/c/923f4dc5df679f678e121c20bf2fd70f7bf3e288
- https://git.kernel.org/stable/c/c8718026ba287168ff9ad0ccc4f9a413062cba36
- https://git.kernel.org/stable/c/cbd86110546f7f730a1f5d7de56c944a336c15c4
