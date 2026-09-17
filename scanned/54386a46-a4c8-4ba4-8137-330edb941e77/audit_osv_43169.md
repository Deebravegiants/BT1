# [M] Execution with Unnecessary Privileges in Kibana Leading to Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-72654
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-72654
Type: osv

## Details
Execution with Unnecessary Privileges (CWE-250) in the Kibana machine learning feature can lead to information disclosure via Privilege Abuse (CAPEC-122). An operation available to users holding only read access to the machine learning feature was performed with an internal service identity rather than the identity of the requesting user. Such a user could therefore receive data from Elasticsearch indices they are not authorized to read. No Elasticsearch cluster or index privileges are required.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-2-security-update-esa-2026-135/390091
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72654.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72654
