# [M] XML External Entity Reference in jbpmmigration

## Summary
Severity: Medium
Advisory: GHSA-vc3x-72q4-g3p5
CVE: CVE-2017-7545
CWE: CWE-611
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vc3x-72q4-g3p5
Type: github-advisory

## Affected
- Maven: `org.jbpm.jbpm5:jbpmmigration` — affected >=0

## Details
It was discovered that the XmlUtils class in jbpmmigration performed expansion of external parameter entities while parsing XML files. A remote attacker could use this flaw to read files accessible to the user running the application server and, potentially, perform other more advanced XML eXternal Entity (XXE) attacks.

The related jbpm-designer project removed use of jbpmmigration completely as a result.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7545
- https://github.com/kiegroup/jbpm-designer/commit/a143f3b92a6a5a527d929d68c02a0c5d914ab81d
- https://access.redhat.com/errata/RHSA-2017:3354
- https://access.redhat.com/errata/RHSA-2017:3355
- https://bugzilla.redhat.com/show_bug.cgi?id=1474822
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7545
- https://github.com/kiegroup/jbpmmigration
