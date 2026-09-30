# [M] FastGPT has Unauthenticated SSRF in /api/core/app/mcpTools/runTool via missing CHECK_INTERNAL_IP default

## Summary
Severity: Medium
Advisory: CVE-2026-40100
Aliases: GHSA-jrhc-f3j7-f8g4
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-10
Source: https://osv.dev/vulnerability/CVE-2026-40100
Type: osv

## Details
FastGPT is an AI Agent building platform. Prior to 4.14.10.3, the /api/core/app/mcpTools/runTool endpoint accepts arbitrary URLs without authentication. The internal IP check in isInternalAddress() only blocks private IPs when CHECK_INTERNAL_IP=true, which is not the default. This allows unauthenticated attackers to perform SSRF against internal network resources. This vulnerability is fixed in 4.14.10.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40100.json
- https://github.com/labring/FastGPT/security/advisories/GHSA-jrhc-f3j7-f8g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40100
