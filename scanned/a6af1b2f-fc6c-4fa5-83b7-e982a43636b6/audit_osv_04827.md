# [H] BIT-espocrm-2022-38844

## Summary
Severity: High
Advisory: BIT-espocrm-2022-38844
Aliases: CVE-2022-38844
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-espocrm-2022-38844
Type: osv

## Affected
- Bitnami: `espocrm` — affected >=7.1.8

## Details
CSV Injection in Create Contacts in EspoCRM 7.1.8 allows remote authenticated users to run system commands via creating contacts with payloads capable of executing system commands. Admin user exporting contacts in CSV file may end up executing the malicious system commands on his system.

## References
- https://medium.com/cybersecurity-valuelabs/espocrm-7-1-8-is-vulnerable-to-csv-injection-4c07494e2a76
