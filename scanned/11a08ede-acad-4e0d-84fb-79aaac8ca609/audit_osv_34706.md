# [C] DataEase is vulnerable to Oracle JNDI Injection

## Summary
Severity: Critical
Advisory: CVE-2025-64164
Aliases: GHSA-q754-4pc2-wjqw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2025-11-06
Source: https://osv.dev/vulnerability/CVE-2025-64164
Type: osv

## Details
Dataease is an open source data visualization analysis tool. In versions 2.10.14 and below, DataEase did not properly filter when establishing JDBC connections to Oracle, resulting in a risk of JNDI injection (Java Naming and Directory Interface injection). This issue is fixed in version 2.10.15.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64164.json
- https://github.com/dataease/dataease/security/advisories/GHSA-q754-4pc2-wjqw
- https://nvd.nist.gov/vuln/detail/CVE-2025-64164
- https://github.com/dataease/dataease/commit/7b68eb3dfccbbd12ec977e6320dbd3e32a7bbfe6
