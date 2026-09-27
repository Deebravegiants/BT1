# [C] BIT-suitecrm-2020-8803

## Summary
Severity: Critical
Advisory: BIT-suitecrm-2020-8803
Aliases: CVE-2020-8803
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-suitecrm-2020-8803
Type: osv

## Affected
- Bitnami: `suitecrm` — affected >=0 <7.11.12

## Details
SuiteCRM through 7.11.11 allows Directory Traversal to include arbitrary .php files within the webroot via add_to_prospect_list.

## References
- http://packetstormsecurity.com/files/156329/SuiteCRM-7.11.11-Broken-Access-Control-Local-File-Inclusion.html
- http://seclists.org/fulldisclosure/2020/Feb/6
- https://suitecrm.com
- https://nvd.nist.gov/vuln/detail/CVE-2020-8803
