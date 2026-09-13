# [C] Kibana Insertion of Sensitive Information into Log File

## Summary
Severity: Critical
Advisory: CVE-2023-31422
CVSS: 9.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-10-26
Source: https://osv.dev/vulnerability/CVE-2023-31422
Type: osv

## Details
An issue was discovered by Elastic whereby sensitive information is recorded in Kibana logs in the event of an error. The issue impacts only Kibana version 8.10.0 when logging in the JSON layout or when the pattern layout is configured to log the %meta pattern. Elastic has released Kibana 8.10.1 which resolves this issue. The error object recorded in the log contains request information, which can include sensitive data, such as authentication credentials, cookies, authorization headers, query params, request paths, and other metadata. Some examples of sensitive data which can be included in the logs are account credentials for kibana_system, kibana-metricbeat, or Kibana end-users.

## References
- https://discuss.elastic.co/t/kibana-8-10-1-security-update/343287
- https://www.elastic.co/community/security
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31422.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-31422
