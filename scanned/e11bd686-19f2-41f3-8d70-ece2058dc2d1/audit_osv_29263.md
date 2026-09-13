# [H] ata: libata-core: Fix double free on error

## Summary
Severity: High
Advisory: CVE-2024-41087
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-41087
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.97, >=6.2.0 <6.6.37, >=6.7.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ata: libata-core: Fix double free on error

If e.g. the ata_port_alloc() call in ata_host_alloc() fails, we will jump
to the err_out label, which will call devres_release_group().
devres_release_group() will trigger a call to ata_host_release().
ata_host_release() calls kfree(host), so executing the kfree(host) in
ata_host_alloc() will lead to a double free:

kernel BUG at mm/slub.c:553!
Oops: invalid opcode: 0000 [#1] PREEMPT SMP NOPTI
CPU: 11 PID: 599 Comm: (udev-worker) Not tainted 6.10.0-rc5 #47
Hardware name: QEMU Standard PC (i440FX + PIIX, 1996), BIOS 1.16.3-2.fc40 04/01/2014
RIP: 0010:kfree+0x2cf/0x2f0
Code: 5d 41 5e 41 5f 5d e9 80 d6 ff ff 4d 89 f1 41 b8 01 00 00 00 48 89 d9 48 89 da
RSP: 0018:ffffc90000f377f0 EFLAGS: 00010246
RAX: ffff888112b1f2c0 RBX: ffff888112b1f2c0 RCX: ffff888112b1f320
RDX: 000000000000400b RSI: ffffffffc02c9de5 RDI: ffff888112b1f2c0
RBP: ffffc90000f37830 R08: 0000000000000000 R09: 0000000000000000
R10: ffffc90000f37610 R11: 617461203a736b6e R12: ffffea00044ac780
R13: ffff888100046400 R14: ffffffffc02c9de5 R15: 0000000000000006
FS:  00007f2f1cabe980(0000) GS:ffff88813b380000(0000) knlGS:0000000000000000
CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
CR2: 00007f2f1c3acf75 CR3: 0000000111724000 CR4: 0000000000750ef0
PKRU: 55555554
Call Trace:
 <TASK>
 ? __die_body.cold+0x19/0x27
 ? die+0x2e/0x50
 ? do_trap+0xca/0x110
 ? do_error_trap+0x6a/0x90
 ? kfree+0x2cf/0x2f0
 ? exc_invalid_op+0x50/0x70
 ? kfree+0x2cf/0x2f0
 ? asm_exc_invalid_op+0x1a/0x20
 ? ata_host_alloc+0xf5/0x120 [libata]
 ? ata_host_alloc+0xf5/0x120 [libata]
 ? kfree+0x2cf/0x2f0
 ata_host_alloc+0xf5/0x120 [libata]
 ata_host_alloc_pinfo+0x14/0xa0 [libata]
 ahci_init_one+0x6c9/0xd20 [ahci]

Ensure that we will not call kfree(host) twice, by performing the kfree()
only if the devres_open_group() call failed.

## References
- https://git.kernel.org/stable/c/010de9acbea58fbcbda08e3793d6262086a493fe
- https://git.kernel.org/stable/c/062e256516d7db5e7dcdef117f52025cd5c456e3
- https://git.kernel.org/stable/c/290073b2b557e4dc21ee74a1e403d9ae79e393a2
- https://git.kernel.org/stable/c/56f1c7e290cd6c69c948fcd2e2a49e6a637ec38f
- https://git.kernel.org/stable/c/5dde5f8b790274723640d29a07c5a97d57d62047
- https://git.kernel.org/stable/c/702c1edbafb2e6f9d20f6d391273b5be09d366a5
- https://git.kernel.org/stable/c/8106da4d88bbaed809e023cc8014b766223d6e76
- https://git.kernel.org/stable/c/ab9e0c529eb7cafebdd31fe1644524e80a48b05d
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41087.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41087
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
