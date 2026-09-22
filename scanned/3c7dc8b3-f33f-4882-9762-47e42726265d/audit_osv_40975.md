# [M] CVE-2026-56412

## Summary
Severity: Medium
Advisory: CVE-2026-56412
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2026-56412
Type: osv

## Details
libexpat before 2.8.2 does not consider XML_TOK_DATA_CHARS in doCdataSection and thus lacks handler call depth tracking for various calls from within handlers in cases of a policy violation. Thus, a use-after-free can occur. NOTE: this issue exists because of an incomplete fix for CVE-2026-50219.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56412.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-56412
- https://github.com/libexpat/libexpat/pull/1278
