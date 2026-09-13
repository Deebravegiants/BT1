# [H] Out-of-bounds Read in mrb_obj_is_kind_of in in mruby/mruby

## Summary
Severity: High
Advisory: CVE-2022-1427
CVSS: 7.7 (CVSS:3.0/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2022-04-22
Source: https://osv.dev/vulnerability/CVE-2022-1427
Type: osv

## Details
Out-of-bounds Read in mrb_obj_is_kind_of in in GitHub repository mruby/mruby prior to 3.2. # Impact: Possible arbitrary code execution if being exploited.

## References
- https://huntr.dev/bounties/23b6f0a9-64f5-421e-a55f-b5b7a671f301
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1427.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-1427
- https://github.com/mruby/mruby/commit/a4d97934d51cb88954cc49161dc1d151f64afb6b
