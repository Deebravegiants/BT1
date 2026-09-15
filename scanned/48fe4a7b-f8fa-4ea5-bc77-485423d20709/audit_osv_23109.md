# [C] CVE-2022-43286

## Summary
Severity: Critical
Advisory: CVE-2022-43286
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-28
Source: https://osv.dev/vulnerability/CVE-2022-43286
Type: osv

## Details
Nginx NJS v0.7.2 was discovered to contain a heap-use-after-free bug caused by illegal memory copy in the function njs_json_parse_iterator_call at njs_json.c.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/43xxx/CVE-2022-43286.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-43286
- https://github.com/nginx/njs/issues/480
- https://github.com/nginx/njs/commit/2ad0ea24a58d570634e09c2e58c3b314505eaa6a
