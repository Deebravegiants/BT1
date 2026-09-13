# [H] CVE-2021-47286

## Summary
Severity: High
Advisory: CVE-2021-47286
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2021-47286
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

bus: mhi: core: Validate channel ID when processing command completions

MHI reads the channel ID from the event ring element sent by the
device which can be any value between 0 and 255. In order to
prevent any out of bound accesses, add a check against the maximum
number of channels supported by the controller and those channels
not configured yet so as to skip processing of that event ring
element.

## References
- https://git.kernel.org/stable/c/3efec3b4b16fc7af25676a94230a8ab2a3bb867c
- https://git.kernel.org/stable/c/546362a9ef2ef40b57c6605f14e88ced507f8dd0
- https://git.kernel.org/stable/c/aed4f5b51aba41e2afd7cfda20a0571a6a67dfe9
