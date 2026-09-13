# [H] picklescan - Arbitrary Code Execution via torch.utils.bottleneck.__main__.run_autograd_prof

## Summary
Severity: High
Advisory: CVE-2025-71345
Aliases: GHSA-4whj-rm5r-c2v8
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71345
Type: osv

## Details
picklescan before 0.0.30 fails to detect malicious pickle files that invoke torch.utils.bottleneck.__main__.run_autograd_prof function. Attackers can embed undetected code in pickle files that executes during deserialization, enabling remote code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71345.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-4whj-rm5r-c2v8
- https://nvd.nist.gov/vuln/detail/CVE-2025-71345
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-torch-utils-bottleneck-main-run-autograd-prof
