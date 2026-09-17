# [M] CVE-2021-47190

## Summary
Severity: Medium
Advisory: CVE-2021-47190
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-10
Source: https://osv.dev/vulnerability/CVE-2021-47190
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

perf bpf: Avoid memory leak from perf_env__insert_btf()

perf_env__insert_btf() doesn't insert if a duplicate BTF id is
encountered and this causes a memory leak. Modify the function to return
a success/error value and then free the memory if insertion didn't
happen.

v2. Adds a return -1 when the insertion error occurs in
    perf_env__fetch_btf. This doesn't affect anything as the result is
    never checked.

## References
- https://git.kernel.org/stable/c/11589d3144bc4e272e0aae46ce8156162e99babc
- https://git.kernel.org/stable/c/4924b1f7c46711762fd0e65c135ccfbcfd6ded1f
- https://git.kernel.org/stable/c/642fc22210a5e59d40b1e4d56d21ec3effd401f2
- https://git.kernel.org/stable/c/ab7c3d8d81c511ddfb27823fb07081c96422b56e
