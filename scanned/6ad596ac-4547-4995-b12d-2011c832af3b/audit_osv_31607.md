# [H] Wazuh Agent and Manager OS Command Injection and Untrusted Search Path

## Summary
Severity: High
Advisory: CVE-2025-15616
Aliases: GHSA-522v-p59v-58gm
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:L/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2025-15616
Type: osv

## Details
Wazuh wazuh-agent and wazuh-manager versions 2.1.0 before 4.8.0 contain multiple shell injection and untrusted search path vulnerabilities that allow attackers to execute arbitrary commands through various components including logcollector configuration, maild SMTP server tags, and Kaspersky AR script parameters. Attackers can exploit these vulnerabilities by injecting malicious commands through configuration files, SMTP server settings, and custom flags to achieve remote code execution on affected systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15616.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-522v-p59v-58gm
- https://nvd.nist.gov/vuln/detail/CVE-2025-15616
- https://www.vulncheck.com/advisories/multiple-vulnerabilities-related-to-shell-injection-and-path-traversal-flaws
