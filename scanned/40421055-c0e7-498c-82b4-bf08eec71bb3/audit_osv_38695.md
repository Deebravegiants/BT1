# [H] CyberPanel < 2.4.5 Unauthenticated API Access via AI Scanner Endpoints

## Summary
Severity: High
Advisory: CVE-2026-41473
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-41473
Type: osv

## Details
CyberPanel versions prior to 2.4.5 contain an authentication bypass vulnerability in the AI Scanner worker API endpoints that allows unauthenticated remote attackers to write arbitrary data to the database by sending requests to the /api/ai-scanner/status-webhook and /api/ai-scanner/callback endpoints. Attackers can exploit the lack of authentication checks to cause denial of service through storage exhaustion, corrupt scan history records, and pollute database fields with malicious data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41473.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41473
- https://www.vulncheck.com/advisories/cyberpanel-unauthenticated-api-access-via-ai-scanner-endpoints
- https://github.com/usmannasir/cyberpanel/commit/8eb29181cb137baa4adb4bba5dce60f601d55a5f
- https://github.com/usmannasir/cyberpanel
- https://itsrez.re/post/cyberpanel-rce
