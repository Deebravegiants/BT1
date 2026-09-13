# [M] AutoGPT SSRF vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-22603
Aliases: GHSA-4c8v-hwxc-2356
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2025-03-10
Source: https://osv.dev/vulnerability/CVE-2025-22603
Type: osv

## Details
AutoGPT is a platform that allows users to create, deploy, and manage continuous artificial intelligence agents that automate complex workflows. Versions prior to autogpt-platform-beta-v0.4.2 contains a server-side request forgery (SSRF) vulnerability inside component (or block) `Send Web Request`. The root cause is  that IPV6 address is not restricted or filtered, which allows attackers to perform a server side request forgery to visit an IPV6 service. autogpt-platform-beta-v0.4.2 fixes the issue.

## References
- https://boatneck-faucet-cba.notion.site/SSRF-of-AutoGPT-153b650a4d88804d923ad65a015a7d61
- https://github.com/Significant-Gravitas/AutoGPT/blob/2121ffd06b26a438706bf642372cc46d81c94ddc/autogpt_platform/backend/backend/util/request.py#L11
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22603.json
- https://github.com/Significant-Gravitas/AutoGPT/security/advisories/GHSA-4c8v-hwxc-2356
- https://nvd.nist.gov/vuln/detail/CVE-2025-22603
- https://github.com/Significant-Gravitas/AutoGPT/commit/26214e1b2c6777e0fae866642b23420adaadd6c4
