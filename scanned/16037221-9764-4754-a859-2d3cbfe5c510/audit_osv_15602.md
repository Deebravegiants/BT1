# [C] CVE-2019-17564

## Summary
Severity: Critical
Advisory: CVE-2019-17564
Aliases: GHSA-69wp-3pm3-hxgg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-01
Source: https://osv.dev/vulnerability/CVE-2019-17564
Type: osv

## Details
Unsafe deserialization occurs within a Dubbo application which has HTTP remoting enabled. An attacker may submit a POST request with a Java object in it to completely compromise a Provider instance of Apache Dubbo, if this instance enables HTTP. This issue affected Apache Dubbo 2.7.0 to 2.7.4, 2.6.0 to 2.6.7, and all 2.5.x versions.

## References
- https://advisory.checkmarx.net/advisory/CX-2020-4275
- https://lists.apache.org/thread.html/r13f7a58fa5d61d729e538a378687118e00c3e229903ba1e7b3a807a2%40%3Cdev.dubbo.apache.org%3E
