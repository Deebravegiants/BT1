# [M] Jenkins item creation restriction bypass vulnerability

## Summary
Severity: Medium
Advisory: GHSA-f9qj-77q2-h5c5
CVE: CVE-2024-47804
CWE: CWE-843, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-f9qj-77q2-h5c5
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <2.462.3
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=2.466 <2.479

## Details
Jenkins provides APIs for fine-grained control of item creation:

- Authorization strategies can prohibit the creation of items of a given type in a given item group (`ACL#hasCreatePermission2`).

- Item types can prohibit creation of new instances in a given item group (`TopLevelItemDescriptor#isApplicableIn(ItemGroup)`).

If an attempt is made to create an item of a prohibited type through the Jenkins CLI or the REST API and either of the above checks fail, Jenkins 2.478 and earlier, LTS 2.462.2 and earlier creates the item in memory, only deleting it from disk.

This allows attackers with Item/Create permission to bypass these restrictions, creating a temporary item. With Item/Configure permission, they can also save the item to persist it.

If an attempt is made to create an item of a prohibited type through the Jenkins CLI or the REST API and either of the above checks fail, Jenkins 2.479, LTS 2.462.3 does not retain the item in memory.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47804
- https://www.jenkins.io/security/advisory/2024-10-02/#SECURITY-3448
