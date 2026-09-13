# [M] Renovate before 44.11.3 Credential Exfiltration via Link Header

## Summary
Severity: Medium
Advisory: CVE-2026-88880
Aliases: GHSA-9hmg-9h89-jhmx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-88880
Type: osv

## Details
Renovate before 44.11.3 fails to validate Link header destinations when following GitLab server pagination, allowing malicious servers to redirect credential-bearing requests. Attackers controlling a compromised GitLab server can specify a Link header pointing to attacker-controlled infrastructure to exfiltrate authentication credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88880.json
- https://github.com/renovatebot/renovate/security/advisories/GHSA-9hmg-9h89-jhmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-88880
- https://www.vulncheck.com/advisories/renovate-before-44.11.3-credential-exfiltration-via-link-header
