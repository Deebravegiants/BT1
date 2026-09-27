# [H] BIT-miniconda-2021-42969

## Summary
Severity: High
Advisory: BIT-miniconda-2021-42969
Aliases: CVE-2021-42969
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-miniconda-2021-42969
Type: osv

## Affected
- Bitnami: `miniconda` — affected >=2021.05.0

## Details
Certain Anaconda3 2021.05 are affected by OS command injection. When a user installs Anaconda, an attacker can create a new file and write something in usercustomize.py. When the user opens the terminal or activates Anaconda, the command will be executed.

## References
- https://yuaneuro.cn/anaconda/anaconda_command_execution.docx
