# [M] CVE-2021-46990

## Summary
Severity: Medium
Advisory: CVE-2021-46990
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-46990
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

powerpc/64s: Fix crashes when toggling entry flush barrier

The entry flush mitigation can be enabled/disabled at runtime via a
debugfs file (entry_flush), which causes the kernel to patch itself to
enable/disable the relevant mitigations.

However depending on which mitigation we're using, it may not be safe to
do that patching while other CPUs are active. For example the following
crash:

  sleeper[15639]: segfault (11) at c000000000004c20 nip c000000000004c20 lr c000000000004c20

Shows that we returned to userspace with a corrupted LR that points into
the kernel, due to executing the partially patched call to the fallback
entry flush (ie. we missed the LR restore).

Fix it by doing the patching under stop machine. The CPUs that aren't
doing the patching will be spinning in the core of the stop machine
logic. That is currently sufficient for our purposes, because none of
the patching we do is to that code or anywhere in the vicinity.

## References
- https://git.kernel.org/stable/c/8382b15864e5014261b4f36c2aa89723612ee058
- https://git.kernel.org/stable/c/dd0d6117052faace5440db20fc37175efe921c7d
- https://git.kernel.org/stable/c/0b4eb172cc12dc102cd0ad013e53ee4463db9508
- https://git.kernel.org/stable/c/5bc00fdda1e934c557351a9c751a205293e68cbf
- https://git.kernel.org/stable/c/aec86b052df6541cc97c5fca44e5934cbea4963b
- https://git.kernel.org/stable/c/d2e3590ca39ccfd8a5a46d8c7f095cb6c7b9ae92
- https://git.kernel.org/stable/c/ee4b7aab93c2631c3bb0753023c5dda592bb666b
- https://git.kernel.org/stable/c/0c25a7bb697f2e6ee65b6d63782f675bf129511a
- https://git.kernel.org/stable/c/2db22ba4e0e103f00e0512e0ecce36ac78c644f8
