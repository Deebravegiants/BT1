# [H] picklescan - Arbitrary Code Execution via numpy.f2py.crackfortran.myeval Detection Bypass

## Summary
Severity: High
Advisory: CVE-2025-71365
Aliases: GHSA-3329-ghmp-jmv5
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2025-71365
Type: osv

## Details
picklescan before 0.0.33 fails to detect malicious pickle files that invoke numpy.f2py.crackfortran.myeval function through the reduce method. Attackers can craft malicious pickle files embedding arbitrary code that evades picklescan detection and executes remote code when loaded.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71365.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-3329-ghmp-jmv5
- https://nvd.nist.gov/vuln/detail/CVE-2025-71365
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-numpy-f2py-crackfortran-myeval-detection-bypass
