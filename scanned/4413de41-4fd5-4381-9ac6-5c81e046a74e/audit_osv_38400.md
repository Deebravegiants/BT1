# [C] Tophat has a Command Injection Vulnerability When Accessing a Maliciously Crafted Tophat Link

## Summary
Severity: Critical
Advisory: CVE-2026-39862
Aliases: GHSA-8x8g-6rv5-mgg2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-39862
Type: osv

## Details
Tophat is a mobile applications testing harness. Prior to 2.5.1, Tophat is affected by remote code execution via crafted tophat:// or http://localhost:29070 URLs. The arguments query parameter flows unsanitized from URL parsing through to /bin/bash -c execution, allowing an attacker to execute arbitrary commands on a developer's macOS workstation. Any developer with Tophat installed is vulnerable. For previously trusted build hosts, no confirmation dialog appears. Attacker commands run with the user's permissions. This vulnerability is fixed in 2.5.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39862.json
- https://github.com/Shopify/tophat/security/advisories/GHSA-8x8g-6rv5-mgg2
- https://nvd.nist.gov/vuln/detail/CVE-2026-39862
- https://github.com/Shopify/tophat/pull/139
