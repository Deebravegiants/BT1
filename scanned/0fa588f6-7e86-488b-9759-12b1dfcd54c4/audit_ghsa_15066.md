# [H] Arbitrary Code Execution in Processwire

## Summary
Severity: High
Advisory: GHSA-2cvg-w29m-j8xc
CVE: CVE-2023-24676
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-2cvg-w29m-j8xc
Type: github-advisory

## Affected
- Packagist: `processwire/processwire` — affected >=0

## Details
An issue found in Processwire 3.0.210 allows attackers to execute arbitrary code and install a reverse shell via the download_zip_url parameter when installing a new module.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24676
- https://github.com/processwire/processwire
- https://medium.com/%40cupc4k3/reverse-shell-via-remote-file-inlusion-in-proccesswire-cms-a8fa5ace3255
