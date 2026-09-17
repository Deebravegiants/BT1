# [M] CVE-2023-40791

## Summary
Severity: Medium
Advisory: CVE-2023-40791
CVSS: 6.3 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-10-16
Source: https://osv.dev/vulnerability/CVE-2023-40791
Type: osv

## Details
extract_user_to_sg in lib/scatterlist.c in the Linux kernel before 6.4.12 fails to unpin pages in a certain situation, as demonstrated by a WARNING for try_grab_page.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.4.12
- https://security.netapp.com/advisory/ntap-20231110-0009/
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f443fd5af5dbd531f880d3645d5dd36976cf087f
- https://lore.kernel.org/linux-crypto/20571.1690369076%40warthog.procyon.org.uk/
- https://lkml.org/lkml/2023/8/3/323
