# [H] igc: don't fail igc_probe() on LED setup error

## Summary
Severity: High
Advisory: CVE-2025-39956
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-39956
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.12.49, >=6.13.0 <6.16.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

igc: don't fail igc_probe() on LED setup error

When igc_led_setup() fails, igc_probe() fails and triggers kernel panic
in free_netdev() since unregister_netdev() is not called. [1]
This behavior can be tested using fault-injection framework, especially
the failslab feature. [2]

Since LED support is not mandatory, treat LED setup failures as
non-fatal and continue probe with a warning message, consequently
avoiding the kernel panic.

[1]
 kernel BUG at net/core/dev.c:12047!
 Oops: invalid opcode: 0000 [#1] SMP NOPTI
 CPU: 0 UID: 0 PID: 937 Comm: repro-igc-led-e Not tainted 6.17.0-rc4-enjuk-tnguy-00865-gc4940196ab02 #64 PREEMPT(voluntary)
 Hardware name: QEMU Standard PC (Q35 + ICH9, 2009), BIOS 1.16.3-debian-1.16.3-2 04/01/2014
 RIP: 0010:free_netdev+0x278/0x2b0
 [...]
 Call Trace:
  <TASK>
  igc_probe+0x370/0x910
  local_pci_probe+0x3a/0x80
  pci_device_probe+0xd1/0x200
 [...]

[2]
 #!/bin/bash -ex

 FAILSLAB_PATH=/sys/kernel/debug/failslab/
 DEVICE=0000:00:05.0
 START_ADDR=$(grep " igc_led_setup" /proc/kallsyms \
         | awk '{printf("0x%s", $1)}')
 END_ADDR=$(printf "0x%x" $((START_ADDR + 0x100)))

 echo $START_ADDR > $FAILSLAB_PATH/require-start
 echo $END_ADDR > $FAILSLAB_PATH/require-end
 echo 1 > $FAILSLAB_PATH/times
 echo 100 > $FAILSLAB_PATH/probability
 echo N > $FAILSLAB_PATH/ignore-gfp-wait

 echo $DEVICE > /sys/bus/pci/drivers/igc/bind

## References
- https://git.kernel.org/stable/c/528eb4e19ec0df30d0c9ae4074ce945667dde919
- https://git.kernel.org/stable/c/bec504867acc7315de9cd96ef9161fa52a25abe8
- https://git.kernel.org/stable/c/f05e82d8553232cef150a6dbb70ed67d162abb2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39956.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39956
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
