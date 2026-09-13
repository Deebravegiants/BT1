# [C] Dataease H2 data source JDBC URL validation bypass leads to remote code execution

## Summary
Severity: Critical
Advisory: CVE-2025-58748
Aliases: GHSA-23qw-9qrh-9rr8
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-09-15
Source: https://osv.dev/vulnerability/CVE-2025-58748
Type: osv

## Details
Dataease is an open source data analytics and visualization platform. In Dataease versions up to 2.10.12 the H2 data source implementation (H2.java) does not verify that a provided JDBC URL starts with jdbc:h2. This lack of validation allows a crafted JDBC configuration that substitutes the Amazon Redshift driver and leverages the socketFactory and socketFactoryArg parameters to invoke org.springframework.context.support.FileSystemXmlApplicationContext or ClassPathXmlApplicationContext with an attacker‑controlled remote XML resource, resulting in remote code execution. Versions up to and including 2.10.12 are affected. The issue is fixed in version 2.10.13. Updating to version 2.10.13 or later is the recommended remediation. No known workarounds exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58748.json
- https://github.com/dataease/dataease/security/advisories/GHSA-23qw-9qrh-9rr8
- https://nvd.nist.gov/vuln/detail/CVE-2025-58748
- https://github.com/dataease/dataease/commit/23a45e72a7abc37d5680b0a7cf691b8df378d4ef
