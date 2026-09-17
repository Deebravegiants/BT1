# [M] CVE-2021-47645

## Summary
Severity: Medium
Advisory: CVE-2021-47645
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47645
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: staging: media: zoran: calculate the right buffer number for zoran_reap_stat_com

On the case tmp_dcim=1, the index of buffer is miscalculated.
This generate a NULL pointer dereference later.

So let's fix the calcul and add a check to prevent this to reappear.

## References
- https://git.kernel.org/stable/c/8dce4b265a5357731058f69645840dabc718c687
- https://git.kernel.org/stable/c/bafec1a6ba4b187a7fcdcfce0faebdc623d4ef8e
- https://git.kernel.org/stable/c/e3b86f4e558cea9eed71d894df2f19b10d60a207
- https://git.kernel.org/stable/c/20811bbe685ca3eddd34b0c750860427d7030910
- https://git.kernel.org/stable/c/20db2ed1e2f9fcd417fa67853e5154f0c2537d6c
- https://git.kernel.org/stable/c/7e76f3ed7ab2ae026c6ef9cc23096a7554af8c52
