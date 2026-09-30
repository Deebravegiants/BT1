# [C] Missing key verification in gost

## Summary
Severity: Critical
Advisory: GHSA-8wxx-35qc-vp6r
CVE: CVE-2024-39223
CWE: CWE-289, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-03
Source: https://github.com/advisories/GHSA-8wxx-35qc-vp6r
Type: github-advisory

## Affected
- Go: `github.com/ginuerzh/gost` — affected >=0

## Details
An authentication bypass in the SSH service of gost v2.11.5 allows attackers to intercept communications via setting the HostKeyCallback function to ssh.InsecureIgnoreHostKey

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39223
- https://github.com/ginuerzh/gost/issues/1034
- https://gist.github.com/nyxfqq/a7242170b1118e78436a62dee4e09e8a
- https://github.com/ginuerzh/gost
- https://github.com/ginuerzh/gost/blob/729d0e70005607dc7c69fc1de62fd8fe21f85355/ssh.go#L229
