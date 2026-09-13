# [H] CVE-2018-8056

## Summary
Severity: High
Advisory: CVE-2018-8056
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-03-11
Source: https://osv.dev/vulnerability/CVE-2018-8056
Type: osv

## Details
Physical path Leakage exists in Western Bridge Cobub Razor 0.8.0 via an invalid channel_name parameter to /index.php?/manage/channel/addchannel or a direct request to /export.php.

## References
- https://github.com/Kyhvedn/CVE_Description/blob/master/Cobub_Razor_0.8.0_physical_path_leakage.md
- https://github.com/cobub/razor/issues/162
- https://www.exploit-db.com/exploits/44495/
