# [M] tracing: Fix race issue between cpu buffer write and swap

## Summary
Severity: Medium
Advisory: CVE-2023-53368
Ecosystem: Linux
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-17
Source: https://osv.dev/vulnerability/CVE-2023-53368
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.10.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tracing: Fix race issue between cpu buffer write and swap

Warning happened in rb_end_commit() at code:
	if (RB_WARN_ON(cpu_buffer, !local_read(&cpu_buffer->committing)))

  WARNING: CPU: 0 PID: 139 at kernel/trace/ring_buffer.c:3142
	rb_commit+0x402/0x4a0
  Call Trace:
   ring_buffer_unlock_commit+0x42/0x250
   trace_buffer_unlock_commit_regs+0x3b/0x250
   trace_event_buffer_commit+0xe5/0x440
   trace_event_buffer_reserve+0x11c/0x150
   trace_event_raw_event_sched_switch+0x23c/0x2c0
   __traceiter_sched_switch+0x59/0x80
   __schedule+0x72b/0x1580
   schedule+0x92/0x120
   worker_thread+0xa0/0x6f0

It is because the race between writing event into cpu buffer and swapping
cpu buffer through file per_cpu/cpu0/snapshot:

  Write on CPU 0             Swap buffer by per_cpu/cpu0/snapshot on CPU 1
  --------                   --------
                             tracing_snapshot_write()
                               [...]

  ring_buffer_lock_reserve()
    cpu_buffer = buffer->buffers[cpu]; // 1. Suppose find 'cpu_buffer_a';
    [...]
    rb_reserve_next_event()
      [...]

                               ring_buffer_swap_cpu()
                                 if (local_read(&cpu_buffer_a->committing))
                                     goto out_dec;
                                 if (local_read(&cpu_buffer_b->committing))
                                     goto out_dec;
                                 buffer_a->buffers[cpu] = cpu_buffer_b;
                                 buffer_b->buffers[cpu] = cpu_buffer_a;
                                 // 2. cpu_buffer has swapped here.

      rb_start_commit(cpu_buffer);
      if (unlikely(READ_ONCE(cpu_buffer->buffer)
          != buffer)) { // 3. This check passed due to 'cpu_buffer->buffer'
        [...]           //    has not changed here.
        return NULL;
      }
                                 cpu_buffer_b->buffer = buffer_a;
                                 cpu_buffer_a->buffer = buffer_b;
                                 [...]

      // 4. Reserve event from 'cpu_buffer_a'.

  ring_buffer_unlock_commit()
    [...]
    cpu_buffer = buffer->buffers[cpu]; // 5. Now find 'cpu_buffer_b' !!!
    rb_commit(cpu_buffer)
      rb_end_commit()  // 6. WARN for the wrong 'committing' state !!!

Based on above analysis, we can easily reproduce by following testcase:
  ``` bash
  #!/bin/bash

  dmesg -n 7
  sysctl -w kernel.panic_on_warn=1
  TR=/sys/kernel/tracing
  echo 7 > ${TR}/buffer_size_kb
  echo "sched:sched_switch" > ${TR}/set_event
  while [ true ]; do
          echo 1 > ${TR}/per_cpu/cpu0/snapshot
  done &
  while [ true ]; do
          echo 1 > ${TR}/per_cpu/cpu0/snapshot
  done &
  while [ true ]; do
          echo 1 > ${TR}/per_cpu/cpu0/snapshot
  done &
  ```

To fix it, IIUC, we can use smp_call_function_single() to do the swap on
the target cpu where the buffer is located, so that above race would be
avoided.

## References
- https://git.kernel.org/stable/c/3163f635b20e9e1fb4659e74f47918c9dddfe64e
- https://git.kernel.org/stable/c/37ca1b686078b00cc4ffa008e2190615f7709b5d
- https://git.kernel.org/stable/c/6182318ac04648b46db9d441fd7d696337fcdd0b
- https://git.kernel.org/stable/c/74c85396bd73eca80b96510b4edf93b9a3aff75f
- https://git.kernel.org/stable/c/89c89da92a60028013f9539be0dcce7e44405a43
- https://git.kernel.org/stable/c/90e037cabc2c2dfc39b3dd9c5b22ea91f995539a
- https://git.kernel.org/stable/c/c5d30d6aa83d99fba8dfdd9cf6c4e4e7a63244db
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53368.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53368
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
