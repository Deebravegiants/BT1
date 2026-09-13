# [H] CVE-2017-8067

## Summary
Severity: High
Advisory: CVE-2017-8067
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-23
Source: https://osv.dev/vulnerability/CVE-2017-8067
Type: osv

## Details
drivers/char/virtio_console.c in the Linux kernel 4.9.x and 4.10.x before 4.10.12 interacts incorrectly with the CONFIG_VMAP_STACK option, which allows local users to cause a denial of service (system crash or memory corruption) or possibly have unspecified other impact by leveraging use of more than one virtual page for a DMA scatterlist.

## References
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.10.12
- http://www.securityfocus.com/bid/97997
- http://www.openwall.com/lists/oss-security/2017/04/16/4
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c4baad50297d84bde1a7ad45e50c73adae4a2192
- https://github.com/torvalds/linux/commit/c4baad50297d84bde1a7ad45e50c73adae4a2192
