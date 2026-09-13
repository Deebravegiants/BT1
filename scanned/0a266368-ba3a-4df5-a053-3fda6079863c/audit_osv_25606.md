# [M] Notepad++ global buffer read overflow in CharDistributionAnalysis::HandleOneChar

## Summary
Severity: Medium
Advisory: CVE-2023-40036
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-08-25
Source: https://osv.dev/vulnerability/CVE-2023-40036
Type: osv

## Details
Notepad++ is a free and open-source source code editor. Versions 8.5.6 and prior are vulnerable to global buffer read overflow in `CharDistributionAnalysis::HandleOneChar`. The exploitability of this issue is not clear. Potentially, it may be used to leak internal memory allocation information. As of time of publication, no known patches are available in existing versions of Notepad++.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/40xxx/CVE-2023-40036.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-40036
- https://securitylab.github.com/advisories/GHSL-2023-092_Notepad__/
