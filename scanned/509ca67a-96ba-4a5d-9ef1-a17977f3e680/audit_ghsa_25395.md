# [M] Infinispan Rest API Does Not Enforce Auth Constraints

## Summary
Severity: Medium
Advisory: GHSA-mvxp-3j62-jqr6
CVE: CVE-2017-2638
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mvxp-3j62-jqr6
Type: github-advisory

## Affected
- Maven: `org.infinispan:infinispan-server-core` — affected >=0 <9.0.0

## Details
It was found that the REST API in Infinispan before version 9.0.0 did not properly enforce auth constraints. An attacker could use this vulnerability to read or modify data in the default cache or a known cache name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2638
- https://github.com/infinispan/infinispan/pull/4936
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-2638
- https://issues.jboss.org/browse/ISPN-7485
- http://rhn.redhat.com/errata/RHSA-2017-1097.html
- http://www.securityfocus.com/bid/97964
