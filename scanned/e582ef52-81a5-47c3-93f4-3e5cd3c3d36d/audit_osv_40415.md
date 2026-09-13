# [H] accel/ethosu: fix OOB write in ethosu_gem_cmdstream_copy_and_validate()

## Summary
Severity: High
Advisory: CVE-2026-53173
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53173
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

accel/ethosu: fix OOB write in ethosu_gem_cmdstream_copy_and_validate()

The command stream parsing loop increments the index variable a second
time when a 64-bit command word is encountered (bit 14 set), but does
not re-check the loop bound before writing the second word:

    for (i = 0; i < size / 4; i++) {
        bocmds[i] = cmds[0];
        if (cmd & 0x4000) {
            i++;
            bocmds[i] = cmds[1];   /* unchecked */
        }
    }

The buffer bocmds is backed by a DMA allocation of exactly size bytes
from drm_gem_dma_create(ddev, size), giving valid indices [0, size/4-1].

When i == size/4 - 1 on entry to an iteration and bit 14 of cmds[0] is
set, bocmds[size/4-1] is written in bounds, i is then incremented to
size/4, and bocmds[size/4] writes four bytes past the end of the
allocation.

Userspace controls both the buffer contents and the size argument via
the ioctl, making this a userspace-triggerable heap out-of-bounds write.

Fix by checking the incremented index against the buffer bound before
the second write and returning -EINVAL if the buffer is too small to
contain the extended command.

## References
- https://git.kernel.org/stable/c/c0837b9cf6eabbad8b8cbddaff1a46a6d0a2e29d
- https://git.kernel.org/stable/c/db6cb3e35cebf487f9a78ebd4cfa4b83708ff40d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53173.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53173
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
