# [C] BIT-vault-2020-35192

## Summary
Severity: Critical
Advisory: BIT-vault-2020-35192
Aliases: CVE-2020-35192
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-vault-2020-35192
Type: osv

## Affected
- Bitnami: `vault` — affected >=0.6.0 <0.11.6

## Details
The official vault docker images before 0.11.6 contain a blank password for a root user. System using the vault docker container deployed by affected versions of the docker image may allow a remote attacker to achieve root access with a blank password.

## References
- https://github.com/koharin/koharin2/blob/main/CVE-2020-35192
- https://nvd.nist.gov/vuln/detail/CVE-2020-35192
