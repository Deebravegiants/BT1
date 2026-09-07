# [C] OS Command Injection in Plexus-utils

## Summary
Severity: Critical
Advisory: GHSA-8vhq-qq4p-grq3
CVE: CVE-2017-1000487
CWE: CWE-78
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8vhq-qq4p-grq3
Type: github-advisory

## Affected
- Maven: `org.codehaus.plexus:plexus-utils` — affected >=0 <3.0.16

## Details
Plexus-utils before 3.0.16 is vulnerable to command injection because it does not correctly process the contents of double quoted strings.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000487
- https://github.com/codehaus-plexus/plexus-utils/commit/b38a1b3a4352303e4312b2bb601a0d7ec6e28f41
- https://www.debian.org/security/2018/dsa-4149
- https://www.debian.org/security/2018/dsa-4146
- https://snyk.io/vuln/SNYK-JAVA-ORGCODEHAUSPLEXUS-31522
- https://lists.debian.org/debian-lts-announce/2018/01/msg00011.html
- https://lists.debian.org/debian-lts-announce/2018/01/msg00010.html
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/rd0e44e8ef71eeaaa3cf3d1b8b41eb25894372e2995ec908ce7624d26%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r9584c4304c888f651d214341a939bd264ed30c9e3d0d30fe85097ecf@%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r9584c4304c888f651d214341a939bd264ed30c9e3d0d30fe85097ecf%40%3Ccommits.pulsar.apache.org%3E
- https://lists.apache.org/thread.html/r2e94f72f53df432302d359fd66cfa9e9efb8d42633d54579a4377e62@%3Cdev.avro.apache.org%3E
- https://lists.apache.org/thread.html/r2e94f72f53df432302d359fd66cfa9e9efb8d42633d54579a4377e62%40%3Cdev.avro.apache.org%3E
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe@%3Ccommits.druid.apache.org%3E
- https://lists.apache.org/thread.html/9317fd092b257a0815434b116a8af8daea6e920b6673f4fd5583d5fe%40%3Ccommits.druid.apache.org%3E
- https://github.com/codehaus-plexus/plexus-utils
- https://access.redhat.com/errata/RHSA-2018:1322
