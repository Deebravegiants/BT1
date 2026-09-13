# [H] CVE-2021-47004

## Summary
Severity: High
Advisory: CVE-2021-47004
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47004
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

f2fs: fix to avoid touching checkpointed data in get_victim()

In CP disabling mode, there are two issues when using LFS or SSR | AT_SSR
mode to select victim:

1. LFS is set to find source section during GC, the victim should have
no checkpointed data, since after GC, section could not be set free for
reuse.

Previously, we only check valid chpt blocks in current segment rather
than section, fix it.

2. SSR | AT_SSR are set to find target segment for writes which can be
fully filled by checkpointed and newly written blocks, we should never
select such segment, otherwise it can cause panic or data corruption
during allocation, potential case is described as below:

 a) target segment has 'n' (n < 512) ckpt valid blocks
 b) GC migrates 'n' valid blocks to other segment (segment is still
    in dirty list)
 c) GC migrates '512 - n' blocks to target segment (segment has 'n'
    cp_vblocks and '512 - n' vblocks)
 d) If GC selects target segment via {AT,}SSR allocator, however there
    is no free space in targe segment.

## References
- https://git.kernel.org/stable/c/105155a8146ddb54c119d8318964eef3859d109d
- https://git.kernel.org/stable/c/1e116f87825f01a6380286472196882746b16f63
- https://git.kernel.org/stable/c/211372b2571520e394b56b431a0705586013b3ff
- https://git.kernel.org/stable/c/61461fc921b756ae16e64243f72af2bfc2e620db
