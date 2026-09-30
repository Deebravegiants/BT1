# [H] BIT-miniconda-2022-26526

## Summary
Severity: High
Advisory: BIT-miniconda-2022-26526
Aliases: CVE-2022-26526
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-miniconda-2022-26526
Type: osv

## Affected
- Bitnami: `miniconda` — affected >=0 <4.11.0

## Details
Anaconda Anaconda3 (Anaconda Distribution) through 2021.11.0.0 and Miniconda3 through 4.11.0 can create a world-writable directory under %PROGRAMDATA% and place that directory into the system PATH environment variable. Thus, for example, local users can gain privileges by placing a Trojan horse file into that directory. (This problem can only happen in a non-default installation. The person who installs the product must specify that it is being installed for all users. Also, the person who installs the product must specify that the system PATH should be changed.

## References
- https://docs.conda.io/en/latest/miniconda.html
- https://github.com/continuumio/anaconda-issues/issues
- https://improsec.com/tech-blog/privilege-escalation-vulnerability-in-anaconda3-and-miniconda3
- https://repo.anaconda.com/miniconda/
