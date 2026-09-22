# [H] CVE-2020-29368

## Summary
Severity: High
Advisory: CVE-2020-29368
Aliases: A-174738029, ASB-A-174738029
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-28
Source: https://osv.dev/vulnerability/CVE-2020-29368
Type: osv

## Details
An issue was discovered in __split_huge_pmd in mm/huge_memory.c in the Linux kernel before 5.7.5. The copy-on-write implementation can grant unintended write access because of a race condition in a THP mapcount check, aka CID-c444eb564fb1.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.5
- https://security.netapp.com/advisory/ntap-20210108-0002/
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2045
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=c444eb564fb16645c172d550359cb3d75fe8a040
