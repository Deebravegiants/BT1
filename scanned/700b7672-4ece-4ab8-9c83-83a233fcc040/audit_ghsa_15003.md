# [C] Files or Directories Accessible to External Parties in ProjectDiscovery

## Summary
Severity: Critical
Advisory: GHSA-q5mg-pc7r-r8cr
CVE: CVE-2024-5262
CWE: CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-05
Source: https://github.com/advisories/GHSA-q5mg-pc7r-r8cr
Type: github-advisory

## Affected
- Go: `github.com/projectdiscovery/interactsh` — affected >=0 <1.2.0

## Details
Files or Directories Accessible to External Parties vulnerability in smb server in ProjectDiscovery Interactsh allows remote attackers to read/write any files in the directory and subdirectories of where the victim runs interactsh-server via anonymous login.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5262
- https://github.com/projectdiscovery/interactsh/pull/874
- https://github.com/projectdiscovery/interactsh/commit/6a0cb98b16636a98712729f3d23e34d8bf7260e7
- https://github.com/projectdiscovery/interactsh
- https://pkg.go.dev/vuln/GO-2024-2907
- https://zuso.ai/advisory/za-2024-01
