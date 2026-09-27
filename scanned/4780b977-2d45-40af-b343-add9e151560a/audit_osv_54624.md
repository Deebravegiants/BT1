# [H] CVE-2024-22705

## Summary
Severity: High
Advisory: CVE-2024-22705
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-23
Source: https://osv.dev/vulnerability/CVE-2024-22705
Type: osv

## Details
An issue was discovered in ksmbd in the Linux kernel before 6.6.10. smb2_get_data_area_len in fs/smb/server/smb2misc.c can cause an smb_strndup_from_utf16 out-of-bounds access because the relationship between Name data and CreateContexts data is mishandled.

## References
- https://cdn.kernel.org/pub/linux/kernel/v6.x/ChangeLog-6.6.10
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=d10c77873ba1e9e6b91905018e29e196fd5f863d
