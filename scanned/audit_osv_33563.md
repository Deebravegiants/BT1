# [M] Apache Commons Configuration: Uncontrolled Resource Consumption when loading untrusted configurations in 1.x

## Summary
Severity: Medium
Advisory: CVE-2025-46392
Aliases: GHSA-pvp8-3xj6-8c6x
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-46392
Type: osv

## Details
Uncontrolled Resource Consumption vulnerability in Apache Commons Configuration 1.x.

There are a number of issues in Apache Commons Configuration 1.x that allow excessive resource consumption when loading untrusted configurations or using unexpected usage patterns. The Apache Commons Configuration team does not intend to fix these issues in 1.x. Apache Commons Configuration 1.x is still safe to use in scenario's where you only load trusted configurations. 


Users that load untrusted configurations or give attackers control over usage patterns are recommended to upgrade to the 2.x version line, which fixes these issues. Apache Commons Configuration 2.x is not a drop-in replacement, but as it uses a separate Maven groupId and Java package namespace they can be loaded side-by-side, making it possible to do a gradual migration.

## References
- https://repo.maven.apache.org/maven2
- https://www.cve.org/CVERecord?id=CVE-2024-29131
- https://www.cve.org/CVERecord?id=CVE-2024-29133
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/46xxx/CVE-2025-46392.json
- https://lists.apache.org/thread/y1pl0mn3opz6kwkm873zshjdxq3dwq5s
- https://nvd.nist.gov/vuln/detail/CVE-2025-46392
