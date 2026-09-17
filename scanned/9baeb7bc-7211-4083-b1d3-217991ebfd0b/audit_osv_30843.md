# [H] LoongArch: Add architecture specific huge_pte_clear()

## Summary
Severity: High
Advisory: CVE-2024-56628
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56628
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

LoongArch: Add architecture specific huge_pte_clear()

When executing mm selftests run_vmtests.sh, there is such an error:

 BUG: Bad page state in process uffd-unit-tests  pfn:00000
 page: refcount:0 mapcount:0 mapping:0000000000000000 index:0x0 pfn:0x0
 flags: 0xffff0000002000(reserved|node=0|zone=0|lastcpupid=0xffff)
 raw: 00ffff0000002000 ffffbf0000000008 ffffbf0000000008 0000000000000000
 raw: 0000000000000000 0000000000000000 00000000ffffffff 0000000000000000
 page dumped because: PAGE_FLAGS_CHECK_AT_FREE flag(s) set
 Modules linked in: snd_seq_dummy snd_seq snd_seq_device rfkill vfat fat
    virtio_balloon efi_pstore virtio_net pstore net_failover failover fuse
    nfnetlink virtio_scsi virtio_gpu virtio_dma_buf dm_multipath efivarfs
 CPU: 2 UID: 0 PID: 1913 Comm: uffd-unit-tests Not tainted 6.12.0 #184
 Hardware name: QEMU QEMU Virtual Machine, BIOS unknown 2/2/2022
 Stack : 900000047c8ac000 0000000000000000 9000000000223a7c 900000047c8ac000
         900000047c8af690 900000047c8af698 0000000000000000 900000047c8af7d8
         900000047c8af7d0 900000047c8af7d0 900000047c8af5b0 0000000000000001
         0000000000000001 900000047c8af698 10b3c7d53da40d26 0000010000000000
         0000000000000022 0000000fffffffff fffffffffe000000 ffff800000000000
         000000000000002f 0000800000000000 000000017a6d4000 90000000028f8940
         0000000000000000 0000000000000000 90000000025aa5e0 9000000002905000
         0000000000000000 90000000028f8940 ffff800000000000 0000000000000000
         0000000000000000 0000000000000000 9000000000223a94 000000012001839c
         00000000000000b0 0000000000000004 0000000000000000 0000000000071c1d
         ...
 Call Trace:
 [<9000000000223a94>] show_stack+0x5c/0x180
 [<9000000001c3fd64>] dump_stack_lvl+0x6c/0xa0
 [<900000000056aa08>] bad_page+0x1a0/0x1f0
 [<9000000000574978>] free_unref_folios+0xbf0/0xd20
 [<90000000004e65cc>] folios_put_refs+0x1a4/0x2b8
 [<9000000000599a0c>] free_pages_and_swap_cache+0x164/0x260
 [<9000000000547698>] tlb_batch_pages_flush+0xa8/0x1c0
 [<9000000000547f30>] tlb_finish_mmu+0xa8/0x218
 [<9000000000543cb8>] exit_mmap+0x1a0/0x360
 [<9000000000247658>] __mmput+0x78/0x200
 [<900000000025583c>] do_exit+0x43c/0xde8
 [<9000000000256490>] do_group_exit+0x68/0x110
 [<9000000000256554>] sys_exit_group+0x1c/0x20
 [<9000000001c413b4>] do_syscall+0x94/0x130
 [<90000000002216d8>] handle_syscall+0xb8/0x158
 Disabling lock debugging due to kernel taint
 BUG: non-zero pgtables_bytes on freeing mm: -16384

On LoongArch system, invalid huge pte entry should be invalid_pte_table
or a single _PAGE_HUGE bit rather than a zero value. And it should be
the same with invalid pmd entry, since pmd_none() is called by function
free_pgd_range() and pmd_none() return 0 by huge_pte_clear(). So single
_PAGE_HUGE bit is also treated as a valid pte table and free_pte_range()
will be called in free_pmd_range().

  free_pmd_range()
        pmd = pmd_offset(pud, addr);
        do {
                next = pmd_addr_end(addr, end);
                if (pmd_none_or_clear_bad(pmd))
                        continue;
                free_pte_range(tlb, pmd, addr);
        } while (pmd++, addr = next, addr != end);

Here invalid_pte_table is used for both invalid huge pte entry and
pmd entry.

## References
- https://git.kernel.org/stable/c/7cd1f5f77925ae905a57296932f0f9ef0dc364f8
- https://git.kernel.org/stable/c/7dfbf011a57b9e1a40f5ce8080a53c497e105c6c
- https://git.kernel.org/stable/c/9b602190cf2d8ac957be0011e418ed6c3b49b9a3
- https://git.kernel.org/stable/c/dba3c45e333a3a2a01395b5f5e5f88f8baba74e4
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56628.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56628
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
