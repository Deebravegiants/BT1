# [H] gadgetfs: ep_io - wait until IRQ finishes

## Summary
Severity: High
Advisory: CVE-2022-50028
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50028
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <4.9.326, >=4.10.0 <4.14.291, >=4.15.0 <4.19.256, >=4.20.0 <5.4.211, >=5.5.0 <5.10.138, >=5.11.0 <5.15.63, >=5.16.0 <5.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

gadgetfs: ep_io - wait until IRQ finishes

after usb_ep_queue() if wait_for_completion_interruptible() is
interrupted we need to wait until IRQ gets finished.

Otherwise complete() from epio_complete() can corrupt stack.

## References
- https://git.kernel.org/stable/c/04cb742d4d8f30dc2e83b46ac317eec09191c68e
- https://git.kernel.org/stable/c/118d967ce00a3d128bf731b35e4e2cb0facf5f00
- https://git.kernel.org/stable/c/2b06d5d97c0e067108a122986767731d40742138
- https://git.kernel.org/stable/c/67a4874461422e633236a0286a01b483cd647113
- https://git.kernel.org/stable/c/77040efe59a141286d090c8a0d37c65a355a1832
- https://git.kernel.org/stable/c/94aadba8d000d5de56af4ce8da3f334f21bf7a79
- https://git.kernel.org/stable/c/9ac14f973cb91f0c01776517e6d50981f32b8038
- https://git.kernel.org/stable/c/ca06b4cde54f8ec8be3aa53fd339bd56e62c12b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50028.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50028
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
