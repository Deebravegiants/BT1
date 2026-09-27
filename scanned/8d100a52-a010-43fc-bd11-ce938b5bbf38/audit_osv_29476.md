# [H] CVE-2024-42651

## Summary
Severity: High
Advisory: CVE-2024-42651
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42651
Type: osv

## Details
NanoMQ v0.17.9 was discovered to contain a heap use-after-free vulnerability via the component sub_Ctx_handle. This vulnerability allows attackers to cause a Denial of Service (DoS) via a crafted SUBSCRIBE message.

## References
- https://github.com/songxpu/bug_report/blob/master/MQTT/NanoMQ/CVE-2024-42651.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42651.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42651
- https://github.com/nanomq/nanomq/issues/1217
- https://github.com/nanomq/nanomq
