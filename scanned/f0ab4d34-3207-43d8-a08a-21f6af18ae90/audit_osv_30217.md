# [M] arm64: probes: Fix uprobes for big-endian kernels

## Summary
Severity: Medium
Advisory: CVE-2024-50194
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-08
Source: https://osv.dev/vulnerability/CVE-2024-50194
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.170, >=5.16.0 <6.1.115, >=6.2.0 <6.6.58, >=6.7.0 <6.11.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

arm64: probes: Fix uprobes for big-endian kernels

The arm64 uprobes code is broken for big-endian kernels as it doesn't
convert the in-memory instruction encoding (which is always
little-endian) into the kernel's native endianness before analyzing and
simulating instructions. This may result in a few distinct problems:

* The kernel may may erroneously reject probing an instruction which can
  safely be probed.

* The kernel may erroneously erroneously permit stepping an
  instruction out-of-line when that instruction cannot be stepped
  out-of-line safely.

* The kernel may erroneously simulate instruction incorrectly dur to
  interpretting the byte-swapped encoding.

The endianness mismatch isn't caught by the compiler or sparse because:

* The arch_uprobe::{insn,ixol} fields are encoded as arrays of u8, so
  the compiler and sparse have no idea these contain a little-endian
  32-bit value. The core uprobes code populates these with a memcpy()
  which similarly does not handle endianness.

* While the uprobe_opcode_t type is an alias for __le32, both
  arch_uprobe_analyze_insn() and arch_uprobe_skip_sstep() cast from u8[]
  to the similarly-named probe_opcode_t, which is an alias for u32.
  Hence there is no endianness conversion warning.

Fix this by changing the arch_uprobe::{insn,ixol} fields to __le32 and
adding the appropriate __le32_to_cpu() conversions prior to consuming
the instruction encoding. The core uprobes copies these fields as opaque
ranges of bytes, and so is unaffected by this change.

At the same time, remove MAX_UINSN_BYTES and consistently use
AARCH64_INSN_SIZE for clarity.

Tested with the following:

| #include <stdio.h>
| #include <stdbool.h>
|
| #define noinline __attribute__((noinline))
|
| static noinline void *adrp_self(void)
| {
|         void *addr;
|
|         asm volatile(
|         "       adrp    %x0, adrp_self\n"
|         "       add     %x0, %x0, :lo12:adrp_self\n"
|         : "=r" (addr));
| }
|
|
| int main(int argc, char *argv)
| {
|         void *ptr = adrp_self();
|         bool equal = (ptr == adrp_self);
|
|         printf("adrp_self   => %p\n"
|                "adrp_self() => %p\n"
|                "%s\n",
|                adrp_self, ptr, equal ? "EQUAL" : "NOT EQUAL");
|
|         return 0;
| }

.... where the adrp_self() function was compiled to:

| 00000000004007e0 <adrp_self>:
|   4007e0:       90000000        adrp    x0, 400000 <__ehdr_start>
|   4007e4:       911f8000        add     x0, x0, #0x7e0
|   4007e8:       d65f03c0        ret

Before this patch, the ADRP is not recognized, and is assumed to be
steppable, resulting in corruption of the result:

| # ./adrp-self
| adrp_self   => 0x4007e0
| adrp_self() => 0x4007e0
| EQUAL
| # echo 'p /root/adrp-self:0x007e0' > /sys/kernel/tracing/uprobe_events
| # echo 1 > /sys/kernel/tracing/events/uprobes/enable
| # ./adrp-self
| adrp_self   => 0x4007e0
| adrp_self() => 0xffffffffff7e0
| NOT EQUAL

After this patch, the ADRP is correctly recognized and simulated:

| # ./adrp-self
| adrp_self   => 0x4007e0
| adrp_self() => 0x4007e0
| EQUAL
| #
| # echo 'p /root/adrp-self:0x007e0' > /sys/kernel/tracing/uprobe_events
| # echo 1 > /sys/kernel/tracing/events/uprobes/enable
| # ./adrp-self
| adrp_self   => 0x4007e0
| adrp_self() => 0x4007e0
| EQUAL

## References
- https://git.kernel.org/stable/c/13f8f1e05f1dc36dbba6cba0ae03354c0dafcde7
- https://git.kernel.org/stable/c/14841bb7a531b96e2dde37423a3b33e75147c60d
- https://git.kernel.org/stable/c/3d2530c65be04e93720e30f191a7cf1a3aa8b51c
- https://git.kernel.org/stable/c/8165bf83b8a64be801d59cd2532b0d1ffed74d00
- https://git.kernel.org/stable/c/b6a638cb600e13f94b5464724eaa6ab7f3349ca2
- https://git.kernel.org/stable/c/cf60d19d40184e43d9a624e55a0da73be09e938d
- https://git.kernel.org/stable/c/cf9ddf9ed94c15564a05bbf6e9f18dffa0c7df80
- https://git.kernel.org/stable/c/e6ab336213918575124d6db43dc5d3554526242e
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50194.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50194
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
