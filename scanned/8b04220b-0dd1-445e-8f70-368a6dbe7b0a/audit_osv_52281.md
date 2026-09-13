# [M] CVE-2021-47276

## Summary
Severity: Medium
Advisory: CVE-2021-47276
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47276
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

ftrace: Do not blindly read the ip address in ftrace_bug()

It was reported that a bug on arm64 caused a bad ip address to be used for
updating into a nop in ftrace_init(), but the error path (rightfully)
returned -EINVAL and not -EFAULT, as the bug caused more than one error to
occur. But because -EINVAL was returned, the ftrace_bug() tried to report
what was at the location of the ip address, and read it directly. This
caused the machine to panic, as the ip was not pointing to a valid memory
address.

Instead, read the ip address with copy_from_kernel_nofault() to safely
access the memory, and if it faults, report that the address faulted,
otherwise report what was in that location.

## References
- https://git.kernel.org/stable/c/862dcc14f2803c556bdd73b43c27b023fafce2fb
- https://git.kernel.org/stable/c/97524384762c1fb9b3ded931498dd2047bd0de81
- https://git.kernel.org/stable/c/acf671ba79c1feccc3ec7cfdcffead4efcec49e7
- https://git.kernel.org/stable/c/0bc62e398bbd9e600959e610def5109957437b28
- https://git.kernel.org/stable/c/3e4ddeb68751fb4fb657199aed9cfd5d02796875
- https://git.kernel.org/stable/c/4aedc2bc2b32c93555f47c95610efb89cc1ec09b
- https://git.kernel.org/stable/c/6c14133d2d3f768e0a35128faac8aa6ed4815051
- https://git.kernel.org/stable/c/7e4e824b109f1d41ccf223fbb0565d877d6223a2
