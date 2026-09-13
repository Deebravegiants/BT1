# [M] Org.jboss.eap:wildfly-ejb3: improper deserialization in jboss marshalling allows remote code execution

## Summary
Severity: Medium
Advisory: CVE-2025-2251
CVSS: 6.2 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:L/I:H/A:H)
Published: 2025-04-07
Source: https://osv.dev/vulnerability/CVE-2025-2251
Type: osv

## Details
A security flaw exists in WildFly and JBoss Enterprise Application Platform (EAP) within the Enterprise JavaBeans (EJB) remote invocation mechanism. This vulnerability stems from untrusted data deserialization handled by JBoss Marshalling. This flaw allows an attacker to send a specially crafted serialized object, leading to remote code execution without requiring authentication.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://access.redhat.com/jbossnetwork/restricted/listSoftware.html
- https://github.com/wildfly/wildfly/releases/tag/36.0.0.Final
- https://issues.redhat.com/browse/WFLY-20550
- https://www.wildfly.org/
- https://access.redhat.com/errata/RHSA-2025:10452
- https://access.redhat.com/errata/RHSA-2025:10453
- https://access.redhat.com/errata/RHSA-2025:10459
- https://access.redhat.com/errata/RHSA-2025:10924
- https://access.redhat.com/errata/RHSA-2025:10925
- https://access.redhat.com/errata/RHSA-2025:10926
- https://access.redhat.com/errata/RHSA-2025:10931
- https://access.redhat.com/security/cve/CVE-2025-2251
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/2xxx/CVE-2025-2251.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-2251
- https://bugzilla.redhat.com/show_bug.cgi?id=2351678
- https://github.com/wildfly/wildfly/pull/18872
