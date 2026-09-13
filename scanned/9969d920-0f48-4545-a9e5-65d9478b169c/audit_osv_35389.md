# [H] picklescan - Arbitrary Code Execution via torch.utils._config_module.load_config Bypass

## Summary
Severity: High
Advisory: CVE-2025-71348
Aliases: GHSA-vv6j-3g6g-2pvj, PYSEC-2026-245
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-21
Source: https://osv.dev/vulnerability/CVE-2025-71348
Type: osv

## Details
picklescan before 0.0.28 fails to detect malicious pickle files that invoke torch.utils._config_module.load_config function within reduce methods. Attackers can craft pickle files embedding arbitrary code that evades detection but executes during pickle.load, enabling remote code execution in supply chain attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71348.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-vv6j-3g6g-2pvj
- https://nvd.nist.gov/vuln/detail/CVE-2025-71348
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-torch-utils-config-module-load-config-bypass
