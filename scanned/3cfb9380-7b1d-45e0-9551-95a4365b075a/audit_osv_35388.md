# [H] picklescan - Undetected Remote Code Execution via numpy.f2py.crackfortran.param_eval

## Summary
Severity: High
Advisory: CVE-2025-71347
Aliases: GHSA-cffc-mxrf-mhh4
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71347
Type: osv

## Details
picklescan before 0.0.33 fails to detect malicious pickle files using numpy.f2py.crackfortran.param_eval function in reduce methods, allowing attackers to bypass security checks. Remote attackers can embed undetected code in pickle files that executes during deserialization, enabling arbitrary code execution in applications loading untrusted pickle data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71347.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-cffc-mxrf-mhh4
- https://nvd.nist.gov/vuln/detail/CVE-2025-71347
- https://www.vulncheck.com/advisories/picklescan-undetected-remote-code-execution-via-numpy-f2py-crackfortran-param-eval
