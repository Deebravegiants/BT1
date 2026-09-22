# [H] CVE-2023-50094

## Summary
Severity: High
Advisory: CVE-2023-50094
Aliases: GHSA-fx7f-f735-vgh4
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-01
Source: https://osv.dev/vulnerability/CVE-2023-50094
Type: osv

## Details
reNgine before 2.1.2 allows OS Command Injection if an adversary has a valid session ID. The attack places shell metacharacters in an api/tools/waf_detector/?url= string. The commands are executed as root via subprocess.check_output.

## References
- https://github.com/yogeshojha/rengine/blob/53d9f505f04861a5040195ea71f20907ff90577a/web/api/views.py#L268-L275
- https://github.com/yogeshojha/rengine/blob/5e120bd5f9dfbd1da82a193e8c9702e483d38d22/web/api/views.py#L195
- https://github.com/yogeshojha/rengine/security
- https://www.mattz.io/posts/cve-2023-50094/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50094.json
- https://github.com/yogeshojha/rengine/security/advisories/GHSA-fx7f-f735-vgh4
- https://nvd.nist.gov/vuln/detail/CVE-2023-50094
- https://github.com/yogeshojha/rengine/commit/3d5f1724dd12cf9861443742e7d7c02ff8c75a6f
- https://github.com/yogeshojha/rengine/commit/edd3c85ee16f93804ad38dac5602549d2d30a93e
- https://github.com/yogeshojha/rengine/releases
