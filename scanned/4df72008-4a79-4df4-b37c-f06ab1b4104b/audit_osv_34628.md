# [H] AutoGPT has SSRF vulnerability in SendDiscordFileBlock

## Summary
Severity: High
Advisory: CVE-2025-62616
Aliases: GHSA-ggc4-4fmm-9hmc
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2025-62616
Type: osv

## Details
AutoGPT is a platform that allows users to create, deploy, and manage continuous artificial intelligence agents that automate complex workflows. Prior to autogpt-platform-beta-v0.6.34, in SendDiscordFileBlock, the third-party library aiohttp.ClientSession().get is used directly to access the URL, but the input URL is not filtered, which will cause SSRF vulnerability. This issue has been patched in autogpt-platform-beta-v0.6.34.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62616.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-ggc4-4fmm-9hmc
- https://nvd.nist.gov/vuln/detail/CVE-2025-62616
