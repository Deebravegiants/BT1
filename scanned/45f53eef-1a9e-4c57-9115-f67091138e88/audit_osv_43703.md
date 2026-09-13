# [H] ring-buffer: Use current_context for safe per-CPU buffer swap

## Summary
Severity: High
Advisory: CVE-2026-74601
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74601
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.5.0 <5.10.266, >=5.11.0 <5.15.217, >=5.16.0 <6.1.184, >=6.2.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ring-buffer: Use current_context for safe per-CPU buffer swap

The ring_buffer_swap_cpu() function currently checks the per-CPU
committing counter to determine if a buffer is actively being written to
before performing the swap. However, there exists a race window where
this check can be bypassed:

    ring_buffer_lock_reserve
        cpu_buffer = buffer->buffers[cpu];       // cpu_buffer_a
        rb_reserve_next_event
            rb_start_commit // inc committing
            if (unlikely(READ_ONCE(cpu_buffer->buffer) != buffer)) {...}
            __rb_reserve_next
                rb_move_tail
                    rb_end_commit(cpu_buffer);   // dec committing => 0
                    /* interrupt hits here, successfully swaps! */
                    local_inc(&cpu_buffer->committing);

    ring_buffer_unlock_commit
        cpu_buffer = buffer->buffers[cpu];      // cpu_buffer_b
        rb_commit
            rb_end_commit
            RB_WARN_ON(cpu_buffer, !local_read(&cpu_buffer->committing))
                                                // triggers warning

The committing counter can temporarily drop to 0 during a single write
operation (within rb_move_tail), creating a window where swap can
succeed even though the write is still in progress. This leads to
inconsistent buffer state and triggers the RB_WARN_ON in rb_commit().

Replace the committing counter check with current_context checks, which
are set at the entry of ring_buffer_lock_reserve() and remain valid
throughout the entire write operation, providing a reliable indicator of
buffer busy state during swap.

## References
- https://git.kernel.org/stable/c/22709117d9ae95e52673685f98caac7c356a8227
- https://git.kernel.org/stable/c/26662bc8fced1d668fa1aa146eda085bfc67bd0b
- https://git.kernel.org/stable/c/597f279b7b4a06412e3d965e98cc36e181cdbede
- https://git.kernel.org/stable/c/5b926fb04cb9ef3156dcf88c69a59d3d1a1c4f9f
- https://git.kernel.org/stable/c/5e6e2a18c20e88167d414f666032792e8bf19b80
- https://git.kernel.org/stable/c/6b524e6b234e45c7f5f90d13b042c6f57f80105c
- https://git.kernel.org/stable/c/ad7e10c7ea89af45ac1bf1814855d45da472703d
- https://git.kernel.org/stable/c/f27bdc43077e4fcb5557dfc315ee8d91e741f483
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74601.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74601
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
