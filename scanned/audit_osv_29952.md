# [H] bpf: Prevent tailcall infinite loop caused by freplace

## Summary
Severity: High
Advisory: CVE-2024-47794
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-01-11
Source: https://osv.dev/vulnerability/CVE-2024-47794
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

bpf: Prevent tailcall infinite loop caused by freplace

There is a potential infinite loop issue that can occur when using a
combination of tail calls and freplace.

In an upcoming selftest, the attach target for entry_freplace of
tailcall_freplace.c is subprog_tc of tc_bpf2bpf.c, while the tail call in
entry_freplace leads to entry_tc. This results in an infinite loop:

entry_tc -> subprog_tc -> entry_freplace --tailcall-> entry_tc.

The problem arises because the tail_call_cnt in entry_freplace resets to
zero each time entry_freplace is executed, causing the tail call mechanism
to never terminate, eventually leading to a kernel panic.

To fix this issue, the solution is twofold:

1. Prevent updating a program extended by an freplace program to a
   prog_array map.
2. Prevent extending a program that is already part of a prog_array map
   with an freplace program.

This ensures that:

* If a program or its subprogram has been extended by an freplace program,
  it can no longer be updated to a prog_array map.
* If a program has been added to a prog_array map, neither it nor its
  subprograms can be extended by an freplace program.

Moreover, an extension program should not be tailcalled. As such, return
-EINVAL if the program has a type of BPF_PROG_TYPE_EXT when adding it to a
prog_array map.

Additionally, fix a minor code style issue by replacing eight spaces with a
tab for proper formatting.

## References
- https://git.kernel.org/stable/c/987aa730bad3e1ef66d9f30182294daa78f6387d
- https://git.kernel.org/stable/c/d6083f040d5d8f8d748462c77e90547097df936e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47794.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-47794
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
