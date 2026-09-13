# [C] CVE-2016-4999

## Summary
Severity: Critical
Advisory: CVE-2016-4999
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-08-05
Source: https://osv.dev/vulnerability/CVE-2016-4999
Type: osv

## Details
SQL injection vulnerability in the getStringParameterSQL method in main/java/org/dashbuilder/dataprovider/sql/dialect/DefaultDialect.java in Dashbuilder before 0.6.0.Beta1 allows remote attackers to execute arbitrary SQL commands via a data set lookup filter in the (1) Data Set Authoring or (2) Displayer editor UI.

## References
- http://www.securityfocus.com/bid/91795
- https://access.redhat.com/errata/RHSA-2016:1428
- https://access.redhat.com/errata/RHSA-2016:1429
- https://github.com/dashbuilder/dashbuilder/commit/8574899e3b6455547b534f570b2330ff772e524b
- https://bugzilla.redhat.com/show_bug.cgi?id=1349990
- https://issues.jboss.org/browse/DASHBUILDE-113
