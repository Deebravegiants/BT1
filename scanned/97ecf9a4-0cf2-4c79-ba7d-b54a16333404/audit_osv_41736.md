# [M] Gitleaks Secret Exfiltration via Non-Hermetic Sprig Template Functions in Report Template Feature

## Summary
Severity: Medium
Advisory: CVE-2026-63728
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-63728
Type: osv

## Details
Gitleaks prior to 8.30.1 contains a template injection vulnerability that allows attackers who can supply or influence report templates to read arbitrary environment variables and exfiltrate sensitive data by leveraging non-hermetic Sprig template functions. Attackers can craft malicious report templates using the env, expandenv, and getHostByName functions to extract credentials, tokens, and API keys from the host process and exfiltrate them through DNS queries, including secrets discovered during the scan itself.

## References
- https://fatihhcelik.github.io/posts/gitleaks-abusing-sprig-for-exfiltration/#the-fix
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63728.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63728
- https://www.vulncheck.com/advisories/gitleaks-secret-exfiltration-via-non-hermetic-sprig-template-functions-in-report-template-feature
- https://github.com/gitleaks/gitleaks/commit/83d9cd684c87d95d656c1458ef04895a7f1cbd8e
- https://github.com/gitleaks/gitleaks
