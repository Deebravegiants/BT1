# [H] BIT-suitecrm-2022-23940

## Summary
Severity: High
Advisory: BIT-suitecrm-2022-23940
Aliases: CVE-2022-23940
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2022-23940
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=8.0.0 <8.0.4

## Details
SuiteCRM through 7.12.1 and 8.x through 8.0.1 allows Remote Code Execution. Authenticated users with access to the Scheduled Reports module can achieve this by leveraging PHP deserialization in the email_recipients property. By using a crafted request, they can create a malicious report, containing a PHP-deserialization payload in the email_recipients field. Once someone accesses this report, the backend will deserialize the content of the email_recipients field and the payload gets executed. Project dependencies include a number of interesting PHP deserialization gadgets (e.g., Monolog/RCE1 from phpggc) that can be used for Code Execution.

## References
- https://docs.suitecrm.com/8.x/admin/releases/8.0/
- https://github.com/manuelz120
- https://nvd.nist.gov/vuln/detail/CVE-2022-23940
