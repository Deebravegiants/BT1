# [M] nanomq: Heap-Buffer-Overflow in webhook_inproc.c via cJSON_Parse OOB Read

## Summary
Severity: Medium
Advisory: CVE-2026-34608
Aliases: GHSA-8p57-jxj9-3qq3
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-02
Source: https://osv.dev/vulnerability/CVE-2026-34608
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. Prior to version 0.24.10, in NanoMQ's webhook_inproc.c, the hook_work_cb() function processes nng messages by parsing the message body with cJSON_Parse(body). The body is obtained from nng_msg_body(msg), which is a binary buffer without a guaranteed null terminator. This leads to an out-of-bounds read (OOB read) as cJSON_Parse reads until it finds a \0, potentially accessing memory beyond the allocated buffer (e.g., nng_msg metadata or adjacent heap/stack). The issue is often masked by nng's allocation padding (extra 32 bytes of zeros for non-power-of-two sizes <1024 or non-aligned). The overflow is reliably triggered when the JSON payload length is a power-of-two >=1024 (no padding added). This issue has been patched in version 0.24.10.

## References
- https://github.com/nanomq/nanomq/releases/tag/0.24.10
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34608.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-8p57-jxj9-3qq3
- https://nvd.nist.gov/vuln/detail/CVE-2026-34608
- https://github.com/nanomq/nanomq/commit/9499a4b2c47998a6aadb69238c18b9e6771b1691
