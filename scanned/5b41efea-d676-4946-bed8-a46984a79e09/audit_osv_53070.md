# [M] CVE-2022-27950

## Summary
Severity: Medium
Advisory: CVE-2022-27950
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-03-28
Source: https://osv.dev/vulnerability/CVE-2022-27950
Type: osv

## Details
In drivers/hid/hid-elo.c in the Linux kernel before 5.16.11, a memory leak exists for a certain hid_parse error condition.

## References
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=817b8b9c5396d2b2d92311b46719aad5d3339dbe
- https://github.com/torvalds/linux/commit/817b8b9c5396d2b2d92311b46719aad5d3339dbe
- https://www.openwall.com/lists/oss-security/2022/03/13/1
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.16.11
