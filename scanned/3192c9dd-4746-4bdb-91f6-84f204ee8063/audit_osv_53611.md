# [M] CVE-2023-0615

## Summary
Severity: Medium
Advisory: CVE-2023-0615
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-06
Source: https://osv.dev/vulnerability/CVE-2023-0615
Type: osv

## Details
A memory leak flaw and potential divide by zero and Integer overflow was found in the Linux kernel V4L2 and vivid test code functionality. This issue occurs when a user triggers ioctls, such as VIDIOC_S_DV_TIMINGS ioctl. This could allow a local user to crash the system if vivid test code enabled.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2166287
