# [H] Logstash Insertion of Sensitive Information into Log File

## Summary
Severity: High
Advisory: BIT-logstash-2023-46672
Aliases: CVE-2023-46672
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-logstash-2023-46672
Type: osv

## Affected
- Bitnami: `logstash` — affected >=8.10.0 <8.11.1

## Details
An issue was identified by Elastic whereby sensitive information is recorded in Logstash logs under specific circumstances.

The prerequisites for the manifestation of this issue are:

  *  Logstash  is configured to log in JSON format https://www.elastic.co/guide/en/logstash/current/running-logstash-command-line.html , which is not the default logging format.


  *  Sensitive data is stored in the Logstash keystore and referenced as a variable in Logstash configuration.

## References
- https://discuss.elastic.co/t/logstash-8-11-1-security-update-esa-2023-26/347191
- https://security.netapp.com/advisory/ntap-20240125-0002/
- https://www.elastic.co/community/security
- https://security.netapp.com/advisory/ntap-20240229-0001/
- https://nvd.nist.gov/vuln/detail/CVE-2023-46672
