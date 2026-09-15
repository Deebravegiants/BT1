# [M] ai-goofish-monitor Unauthenticated Arbitrary File Read via GET /api/prompts/

## Summary
Severity: Medium
Advisory: CVE-2026-10044
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-10044
Type: osv

## Details
Usagi-org ai-goofish-monitor contains an unauthenticated arbitrary file read vulnerability in the GET /api/prompts/{filename} endpoint on Windows deployments that allows unauthenticated remote attackers to read arbitrary files by supplying absolute Windows paths or backslash-based traversal sequences. Attackers can bypass the incomplete path traversal guard, which only blocks forward slashes and '..', by providing absolute paths such as Windows system file locations, causing os.path.join to discard the intended prompts directory prefix and expose files accessible to the application process.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10044.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-10044
- https://www.vulncheck.com/advisories/ai-goofish-monitor-unauthenticated-arbitrary-file-read-via-get-api-prompts
- https://github.com/Usagi-org/ai-goofish-monitor/issues/488
- https://github.com/Usagi-org/ai-goofish-monitor/pull/489
- https://github.com/Usagi-org/ai-goofish-monitor/commit/f85d140b6b45029d9a0925feb96dad733b41396d
