# [H] camel-infinispan Vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-xfxp-ppx7-cqrp
CVE: CVE-2026-6857
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-xfxp-ppx7-cqrp
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-infinispan` — affected >=0 <4.20.0

## Details
A flaw was found in camel-infinispan. This vulnerability involves unsafe deserialization in the ProtoStream remote aggregation repository. A remote attacker with low privileges could exploit this by sending specially crafted data, leading to arbitrary code execution. This allows the attacker to gain full control over the affected system, impacting its confidentiality, integrity, and availability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6857
- https://github.com/apache/camel/commit/ec297f89065b6cfc2682487a96411692d6c296e2
- https://access.redhat.com/errata/RHSA-2026:17668
- https://access.redhat.com/errata/RHSA-2026:22453
- https://access.redhat.com/security/cve/CVE-2026-6857
- https://bugzilla.redhat.com/show_bug.cgi?id=2460003
- https://github.com/apache/camel
