# [H] ncnn: Out-of-bounds heap write in ParamDict::load_param via unchecked negative parameter id

## Summary
Severity: High
Advisory: CVE-2026-50144
Aliases: GHSA-jxmc-3mv6-7pwr
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-50144
Type: osv

## Details
ncnn is a high-performance neural network inference framework optimized for the mobile platform. In commit e54f7b1f88434e1d844ea0551b880a1cfb079ce1 and earlier, ncnn allows an out-of-bounds heap write in ncnn::ParamDict::load_param() when Net::load_param() loads a malicious .param model file because the parsed parameter id is checked only against id >= NCNN_MAX_PARAM_COUNT, allowing a negative id to index before the params[NCNN_MAX_PARAM_COUNT] array. This vulnerability is fixed by commit 5a0288f255daa6c3294f77109f67718e434ec020.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50144.json
- https://github.com/Tencent/ncnn/security/advisories/GHSA-jxmc-3mv6-7pwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-50144
- https://github.com/Tencent/ncnn/commit/5a0288f255daa6c3294f77109f67718e434ec020
