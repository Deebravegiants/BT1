# [H] NanoMQ has a Use After Free vulnerability via sub info list

## Summary
Severity: High
Advisory: CVE-2025-59946
Aliases: GHSA-xg37-23w7-72p5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-12-27
Source: https://osv.dev/vulnerability/CVE-2025-59946
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an Edge Messaging Platform. Prior to version 0.24.2, there is a classical data racing issue about sub info list which could result in heap use after free crash. This issue has been patched in version 0.24.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59946.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-xg37-23w7-72p5
- https://nvd.nist.gov/vuln/detail/CVE-2025-59946
- https://github.com/nanomq/nanomq/issues/1863
