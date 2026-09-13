# [M] CVE-2026-50219

## Summary
Severity: Medium
Advisory: CVE-2026-50219
CVSS: 4.9 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-06-04
Source: https://osv.dev/vulnerability/CVE-2026-50219
Type: osv

## Details
libexpat before 2.8.2 lacks handler call depth tracking for calls to XML_GetBuffer, XML_Parse, XML_ParseBuffer, XML_ParserFree, or XML_ParserReset from within handlers in cases of a policy violation. Thus, a use-after-free can occur,

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/50xxx/CVE-2026-50219.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-50219
- https://github.com/libexpat/libexpat/pull/1246
