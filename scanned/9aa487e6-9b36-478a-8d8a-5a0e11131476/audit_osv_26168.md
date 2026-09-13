# [H] CVE-2023-52251

## Summary
Severity: High
Advisory: CVE-2023-52251
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-25
Source: https://osv.dev/vulnerability/CVE-2023-52251
Type: osv

## Details
An issue discovered in provectus kafka-ui 0.4.0 through 0.7.2 allows remote attackers to execute arbitrary code via the q parameter of /api/clusters/local/topics/{topic}/messages. No fixed release is available; the project has had no commit since 2024-04-08.

## References
- http://packetstormsecurity.com/files/177214/Kafka-UI-0.7.1-Command-Injection.html
- https://github.com/provectus/kafka-ui/blob/v0.7.2/kafka-ui-api/src/main/java/com/provectus/kafka/ui/emitter/MessageFilters.java
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52251.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52251
- https://github.com/github/advisory-database/issues/9400
- https://github.com/google/osv.dev/issues/5988
- https://github.com/kafbat/kafka-ui/commit/11a57d14
- https://github.com/BobTheShoplifter/CVE-2023-52251-POC
