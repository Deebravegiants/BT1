# [H] scsi: mpt3sas: Avoid test/set_bit() operating in non-allocated memory

## Summary
Severity: High
Advisory: CVE-2024-40901
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40901
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: mpt3sas: Avoid test/set_bit() operating in non-allocated memory

There is a potential out-of-bounds access when using test_bit() on a single
word. The test_bit() and set_bit() functions operate on long values, and
when testing or setting a single word, they can exceed the word
boundary. KASAN detects this issue and produces a dump:

	 BUG: KASAN: slab-out-of-bounds in _scsih_add_device.constprop.0 (./arch/x86/include/asm/bitops.h:60 ./include/asm-generic/bitops/instrumented-atomic.h:29 drivers/scsi/mpt3sas/mpt3sas_scsih.c:7331) mpt3sas

	 Write of size 8 at addr ffff8881d26e3c60 by task kworker/u1536:2/2965

For full log, please look at [1].

Make the allocation at least the size of sizeof(unsigned long) so that
set_bit() and test_bit() have sufficient room for read/write operations
without overwriting unallocated memory.

[1] Link: https://lore.kernel.org/all/ZkNcALr3W3KGYYJG@gmail.com/

## References
- https://git.kernel.org/stable/c/0081d2b3ae0a17a86b8cc0fa3c8bdc54e233ba16
- https://git.kernel.org/stable/c/18abb5db0aa9b2d48f7037a88b41af2eef821674
- https://git.kernel.org/stable/c/19649e49a6df07cd2e03e0a11396fd3a99485ec2
- https://git.kernel.org/stable/c/4254dfeda82f20844299dca6c38cbffcfd499f41
- https://git.kernel.org/stable/c/46bab2bcd771e725ff5ca3a68ba68cfeac45676c
- https://git.kernel.org/stable/c/521f333e644c4246ca04a4fc4772edc53dd2a801
- https://git.kernel.org/stable/c/9079338c5a0d1f1fee34fb1c9e99b754efe414c5
- https://git.kernel.org/stable/c/e9bce7c751f6d6c7be88c0bc081a66aaf61a23ee
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40901.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40901
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
