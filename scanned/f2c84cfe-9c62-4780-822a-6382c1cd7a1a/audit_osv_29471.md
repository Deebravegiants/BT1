# [H] CVE-2024-42644

## Summary
Severity: High
Advisory: CVE-2024-42644
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42644
Type: osv

## Details
FlashMQ v1.14.0 was discovered to contain an assertion failure in the function PublishCopyFactory::getNewPublish, which occurs when the QoS value of the publish object is greater than 0.

## References
- https://github.com/songxpu/bug_report/blob/master/MQTT/FlashMQ/cve-2024-42644.md
- https://www.flashmq.org/2024/06/17/flashmq-1-15-1-released/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42644.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42644
- https://github.com/halfgaar/FlashMQ
