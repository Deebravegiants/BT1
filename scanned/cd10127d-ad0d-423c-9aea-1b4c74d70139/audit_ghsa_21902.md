# [M] Wildfly logs plaintext passwords

## Summary
Severity: Medium
Advisory: GHSA-jw3v-5ch2-wfmm
CVE: CVE-2020-25640
CWE: CWE-209, CWE-532
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-jw3v-5ch2-wfmm
Type: github-advisory

## Affected
- Maven: `org.wildfly:wildfly-parent` — affected >=0 <21.0.0.Final

## Details
A flaw was discovered in WildFly before 21.0.0.Final where, Resource adapter logs plain text JMS password at warning level on connection error, inserting sensitive information in the log file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25640
- https://github.com/amqphub/amqp-10-resource-adapter/issues/13
- https://bugzilla.redhat.com/show_bug.cgi?id=1881637
- https://security.netapp.com/advisory/ntap-20201210-0001
