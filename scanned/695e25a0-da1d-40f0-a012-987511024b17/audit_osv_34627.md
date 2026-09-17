# [H] AutoGPT has SSRF vulnerability in ReadRSSFeedBlock

## Summary
Severity: High
Advisory: CVE-2025-62615
Aliases: GHSA-r55v-q5pc-j57f
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2025-62615
Type: osv

## Details
AutoGPT is a platform that allows users to create, deploy, and manage continuous artificial intelligence agents that automate complex workflows. Prior to autogpt-platform-beta-v0.6.34, in RSSFeedBlock, the third-party library urllib.request.urlopen is used directly to access the URL, but the input URL is not filtered, which will cause SSRF vulnerability. This issue has been patched in autogpt-platform-beta-v0.6.34.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62615.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-r55v-q5pc-j57f
- https://nvd.nist.gov/vuln/detail/CVE-2025-62615
