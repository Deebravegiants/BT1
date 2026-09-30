# [H] picklescan - Arbitrary Code Execution via Undetected ensurepip._run_pip Function

## Summary
Severity: High
Advisory: CVE-2025-71344
Aliases: GHSA-xp4f-hrf8-rxw7, PYSEC-2026-1792
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-22
Source: https://osv.dev/vulnerability/CVE-2025-71344
Type: osv

## Details
picklescan before 0.0.30 (affected versions 0.0.26 and earlier) fails to detect the ensurepip._run_pip built-in function when scanning pickle files, allowing attackers to execute arbitrary code. Malicious pickle files embedding ensurepip._run_pip calls in __reduce__ methods bypass picklescan detection and achieve remote code execution upon pickle.load() invocation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71344.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-xp4f-hrf8-rxw7
- https://nvd.nist.gov/vuln/detail/CVE-2025-71344
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-undetected-ensurepip-run-pip-function
