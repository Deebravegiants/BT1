# [M] NanoMQ has Heap Buffer Overflow in URI Parameter Parsing

## Summary
Severity: Medium
Advisory: CVE-2026-32135
Aliases: GHSA-6w96-9qw7-m599
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-20
Source: https://osv.dev/vulnerability/CVE-2026-32135
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. Versions prior to 0.24.11 have a remotely triggerable heap buffer overflow in the `uri_param_parse` function of NanoMQ's REST API. The vulnerability occurs due to an off-by-one error when allocating memory for query parameter keys and values, allowing an attacker to write a null byte beyond the allocated buffer. This can be triggered via a crafted HTTP request. Version 0.24.11 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32135.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-6w96-9qw7-m599
- https://nvd.nist.gov/vuln/detail/CVE-2026-32135
- https://github.com/nanomq/nanomq/issues/2247
- https://github.com/nanomq/nanomq/commit/69a97b3b39cc218f044f1c8896f4d3d8757bb394
