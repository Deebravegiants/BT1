# [C] conda-forge openssl-feedstock writable OPENSSLDIR

## Summary
Severity: Critical
Advisory: CVE-2025-35471
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-05-13
Source: https://osv.dev/vulnerability/CVE-2025-35471
Type: osv

## Details
conda-forge openssl-feedstock before 066e83c (2024-05-20), on Microsoft Windows, configures OpenSSL to use an OPENSSLDIR file path that can be written to by non-privilged local users. By writing a specially crafted openssl.cnf file in OPENSSLDIR, a non-privileged local user can execute arbitrary code with the privileges of the user or process loading openssl-feedstock DLLs. Miniforge before 24.5.0 is also affected.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/35xxx/CVE-2025-35471.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-35471
- https://github.com/conda-forge/openssl-feedstock/issues/201
- https://github.com/conda-forge/openssl-feedstock/commit/066e83c5226bafe90a9c0575b077ce30cd5f5921
