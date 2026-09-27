# [H] CVE-2023-26544

## Summary
Severity: High
Advisory: CVE-2023-26544
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-25
Source: https://osv.dev/vulnerability/CVE-2023-26544
Type: osv

## Details
In the Linux kernel 6.0.8, there is a use-after-free in run_unpack in fs/ntfs3/run.c, related to a difference between NTFS sector size and media sector size.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=887bfc546097fbe8071dac13b2fef73b77920899
- https://security.netapp.com/advisory/ntap-20230316-0010/
- https://bugzilla.suse.com/show_bug.cgi?id=1208697
- https://lkml.org/lkml/2023/2/20/128
