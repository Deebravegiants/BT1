# [M] BIT-miniconda-2023-35845

## Summary
Severity: Medium
Advisory: BIT-miniconda-2023-35845
Aliases: CVE-2023-35845
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-miniconda-2023-35845
Type: osv

## Affected
- Bitnami: `miniconda` — affected >=2023.03-1.0

## Details
Anaconda 3 2023.03-1-Linux allows local users to disrupt TLS certificate validation by modifying the cacert.pem file used by the installed pip program. This occurs because many files are installed as world-writable on Linux, ignoring umask, even when these files are installed as root. Miniconda is also affected.

## References
- https://uponfurtherinvestigation.blogspot.com/2023/06/cve-2023-35845-anaconda3-creates.html
