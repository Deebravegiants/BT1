# [H] picklescan - Remote Code Execution via Undetected trace.Trace.runctx in Pickle Files

## Summary
Severity: High
Advisory: CVE-2025-71352
Aliases: GHSA-g344-hcph-8vgg
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2025-71352
Type: osv

## Details
picklescan before 0.0.29 fails to detect the built-in Python trace.Trace.runctx function when used in pickle file reduce methods, allowing attackers to execute arbitrary code. Remote attackers can craft malicious pickle files with trace.Trace.runctx payloads that bypass picklescan detection and execute code upon pickle.load() invocation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71352.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-g344-hcph-8vgg
- https://nvd.nist.gov/vuln/detail/CVE-2025-71352
- https://www.vulncheck.com/advisories/picklescan-remote-code-execution-via-undetected-trace-trace-runctx-in-pickle-files
