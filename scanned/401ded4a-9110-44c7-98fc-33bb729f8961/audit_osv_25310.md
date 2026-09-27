# [H] CVE-2023-33657

## Summary
Severity: High
Advisory: CVE-2023-33657
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-06-08
Source: https://osv.dev/vulnerability/CVE-2023-33657
Type: osv

## Details
A use-after-free vulnerability exists in NanoMQ 0.17.2. The vulnerability can be triggered by calling the function nni_mqtt_msg_get_publish_property() in the file mqtt_msg.c. This vulnerability is caused by improper data tracing, and an attacker could exploit it to cause a denial of service attack.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/33xxx/CVE-2023-33657.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-33657
- https://github.com/emqx/nanomq/issues/1165#issue-1668648319
- https://github.com/emqx/nanomq/pull/1187
- https://github.com/emqx/nanomq
