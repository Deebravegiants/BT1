# [M] CVE-2021-20328

## Summary
Severity: Medium
Advisory: CVE-2021-20328
Aliases: GHSA-rghw-6px2-fgwc
CVSS: 6.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-02-25
Source: https://osv.dev/vulnerability/CVE-2021-20328
Type: osv

## Details
Specific versions of the Java driver that support client-side field level encryption (CSFLE) fail to perform correct host name verification on the KMS server’s certificate. This vulnerability in combination with a privileged network position active MITM attack could result in interception of traffic between the Java driver and the KMS service rendering Field Level Encryption ineffective. This issue was discovered during internal testing and affects all versions of the Java driver that support CSFLE. The Java async, Scala, and reactive streams drivers are not impacted. This vulnerability does not impact driver traffic payloads with CSFLE-supported key services originating from applications residing inside the AWS, GCP, and Azure network fabrics due to compensating controls in these environments. This issue does not impact driver workloads that don’t use Field Level Encryption.

## References
- https://jira.mongodb.org/browse/JAVA-4017
