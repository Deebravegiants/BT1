# [C] MindsDB can be made to not verify SSL certificates

## Summary
Severity: Critical
Advisory: GHSA-8hx6-qv6f-xgcw
CVE: CVE-2023-38699
CWE: CWE-311
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-08-01
Source: https://github.com/advisories/GHSA-8hx6-qv6f-xgcw
Type: github-advisory

## Affected
- PyPI: `MindsDB` — affected >=0 <23.7.4.0

## Details
### Summary
MindsDB's AI Virtual Database allows developers to connect any AI/ML model to any datasource. Prior to version 23.7.4.0, a call to requests with `verify=False` disables SSL certificate checks. This rule enforces always verifying SSL certificates for methods in the Requests library. In version 23.7.4.0, certificates are validated by default, which is the desired behavior

Encryption in general is typically critical to the security of many applications. Using TLS can significantly increase security by guaranteeing the identity of the party you are communicating with. This is accomplished by one or both parties presenting trusted certificates during the connection initialization phase of TLS.

It is important to note that modules such as httplib within the Python standard library did not verify certificate chains until it was fixed in 2.7.9 release.

### Details
Severity: Critical

## References
- https://github.com/mindsdb/mindsdb/security/advisories/GHSA-8hx6-qv6f-xgcw
- https://nvd.nist.gov/vuln/detail/CVE-2023-38699
- https://github.com/mindsdb/mindsdb/commit/083afcf6567cf51aa7d89ea892fd97689919053b
- https://github.com/mindsdb/mindsdb
- https://github.com/mindsdb/mindsdb/releases/tag/v23.7.4.0
- https://github.com/pypa/advisory-database/tree/main/vulns/mindsdb/PYSEC-2023-140.yaml
