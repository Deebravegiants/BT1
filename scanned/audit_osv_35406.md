# [H] Picklescan - Arbitrary Code Execution via numpy.f2py.crackfortran.getlincoef Gadget

## Summary
Severity: High
Advisory: CVE-2025-71372
Aliases: GHSA-rrxm-2pvv-m66x
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-04
Source: https://osv.dev/vulnerability/CVE-2025-71372
Type: osv

## Details
Picklescan before 0.0.33 fails to detect the numpy.f2py.crackfortran.getlincoef gadget in pickle __reduce__ methods, allowing arbitrary code execution. Attackers can craft malicious pickle files that execute arbitrary Python code when loaded, bypassing Picklescan's safety checks and enabling supply-chain poisoning of shared model files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71372.json
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-rrxm-2pvv-m66x
- https://nvd.nist.gov/vuln/detail/CVE-2025-71372
- https://www.vulncheck.com/advisories/picklescan-arbitrary-code-execution-via-numpy-f2py-crackfortran-getlincoef-gadget
