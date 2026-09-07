# [H] Deserialization of Untrusted Data in Spring Batch

## Summary
Severity: High
Advisory: GHSA-4ph4-q9r5-6wm6
CVE: CVE-2020-5411
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4ph4-q9r5-6wm6
Type: github-advisory

## Affected
- Maven: `org.springframework.batch:spring-batch-core` — affected >=4.0.0 <4.2.3

## Details
When configured to enable default typing, Jackson contained a deserialization vulnerability that could lead to arbitrary code execution. Jackson fixed this vulnerability by blacklisting known "deserialization gadgets". Spring Batch configures Jackson with global default typing enabled which means that through the previous exploit, arbitrary code could be executed if all of the following is true: * Spring Batch's Jackson support is being leveraged to serialize a job's ExecutionContext. * A malicious user gains write access to the data store used by the JobRepository (where the data to be deserialized is stored). In order to protect against this type of attack, Jackson prevents a set of untrusted gadget classes from being deserialized. Spring Batch should be proactive against blocking unknown "deserialization gadgets" when enabling default typing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-5411
- https://github.com/spring-projects/spring-batch
- https://tanzu.vmware.com/security/cve-2020-5411
