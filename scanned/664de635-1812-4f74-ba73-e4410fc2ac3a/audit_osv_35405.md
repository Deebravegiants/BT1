# [H] picklescan - Remote Code Execution via torch.jit.unsupported_tensor_ops.execWrapper

## Summary
Severity: High
Advisory: CVE-2025-71370
Aliases: GHSA-vr7h-p6mm-wpmh
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2025-71370
Type: osv

## Details
picklescan before 0.0.28 fails to detect malicious torch.jit.unsupported_tensor_ops.execWrapper function calls embedded in pickle files. Attackers can craft malicious pickle files that bypass picklescan detection and execute arbitrary code when loaded via pickle.load().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71370.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-vr7h-p6mm-wpmh
- https://nvd.nist.gov/vuln/detail/CVE-2025-71370
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-torch-jit-unsupported-tensor-ops-execwrapper
