# [M] BIT-espocrm-2022-38846

## Summary
Severity: Medium
Advisory: BIT-espocrm-2022-38846
Aliases: CVE-2022-38846
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-espocrm-2022-38846
Type: osv

## Affected
- Bitnami: `espocrm` — affected >=7.1.8

## Details
EspoCRM version 7.1.8 is vulnerable to Missing Secure Flag allowing the browser to send plain text cookies over an insecure channel (HTTP). An attacker may capture the cookie from the insecure channel using MITM attack.

## References
- https://medium.com/cybersecurity-valuelabs/espocrm-7-1-8-is-vulnerable-to-missing-secure-flag-1664bac5ffe4
