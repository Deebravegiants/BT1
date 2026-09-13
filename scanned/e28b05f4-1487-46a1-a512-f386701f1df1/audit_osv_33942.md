# [C] Potential heap-buffer overflow vulnerability in NotepadNext

## Summary
Severity: Critical
Advisory: CVE-2025-52939
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:N/AU:Y/R:U/V:C/RE:M/U:Red)
Published: 2025-06-23
Source: https://osv.dev/vulnerability/CVE-2025-52939
Type: osv

## Details
Out-of-bounds Write vulnerability in dail8859 NotepadNext (src/lua/src modules). This vulnerability is associated with program files ldebug.C, lvm.C.

This issue affects NotepadNext: through v0.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/52xxx/CVE-2025-52939.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-52939
- https://github.com/dail8859/NotepadNext/commit/3e928d91b8fc8bb5c77801ee8652f41e98d12571
- https://github.com/dail8859/NotepadNext/pull/757/files
- https://github.com/dail8859/NotepadNext
