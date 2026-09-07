# [M] PicketLink does not properly check role based authorization

## Summary
Severity: Medium
Advisory: GHSA-9qhq-j4xm-cw48
CVE: CVE-2015-3158
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-9qhq-j4xm-cw48
Type: github-advisory

## Affected
- Maven: `org.picketlink:picketlink-tomcat-common` — affected >=0 <2.7.1.Final

## Details
The `invokeNextValve` function in `identity/federation/bindings/tomcat/idp/AbstractIDPValve.java` in PicketLink before 2.7.1.Final does not properly check role based authorization, which allows remote authenticated users to gain access to restricted application resources via a (1) direct request or (2) request through an SP initiated flow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-3158
- https://github.com/picketlink/picketlink-bindings/pull/124
- https://github.com/picketlink/picketlink-bindings/commit/ae6ff4adfc562880e714a089983054b47610ecec
- https://bugzilla.redhat.com/show_bug.cgi?id=1216123
- https://github.com/picketlink/picketlink-bindings
- https://issues.jboss.org/browse/PLINK-708
- http://rhn.redhat.com/errata/RHSA-2015-1669.html
- http://rhn.redhat.com/errata/RHSA-2015-1670.html
- http://rhn.redhat.com/errata/RHSA-2015-1671.html
- http://rhn.redhat.com/errata/RHSA-2015-1672.html
- http://rhn.redhat.com/errata/RHSA-2015-1673.html
