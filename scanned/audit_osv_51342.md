# [H] CVE-2021-28952

## Summary
Severity: High
Advisory: CVE-2021-28952
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-03-20
Source: https://osv.dev/vulnerability/CVE-2021-28952
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.11.8. The sound/soc/qcom/sdm845.c soundwire device driver has a buffer overflow when an unexpected port ID number is encountered, aka CID-1c668e1c0a0f. (This has been fixed in 5.12-rc4.)

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4VCKIOXCOZGXBEZMO5LGGV5MWCHO6FT3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PTRNPQTZ4GVS46SZ4OBXY5YDOGVPSTGQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/T2S3I4SLRNRUQDOFYUS6IUAZMQNMPNLG/
- https://lore.kernel.org/alsa-devel/20210309142129.14182-2-srinivas.kandagatla%40linaro.org/
- https://security.netapp.com/advisory/ntap-20210430-0003/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=1c668e1c0a0f74472469cd514f40c9012b324c31
