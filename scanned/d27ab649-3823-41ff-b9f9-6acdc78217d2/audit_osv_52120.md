# [M] CVE-2021-47096

## Summary
Severity: Medium
Advisory: CVE-2021-47096
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-03-04
Source: https://osv.dev/vulnerability/CVE-2021-47096
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: rawmidi - fix the uninitalized user_pversion

The user_pversion was uninitialized for the user space file structure
in the open function, because the file private structure use
kmalloc for the allocation.

The kernel ALSA sequencer code clears the file structure, so no additional
fixes are required.

BugLink: https://github.com/alsa-project/alsa-lib/issues/178

## References
- https://git.kernel.org/stable/c/b398fcbe4de1e1100867fdb6f447c6fbc8fe7085
- https://git.kernel.org/stable/c/39a8fc4971a00d22536aeb7d446ee4a97810611b
