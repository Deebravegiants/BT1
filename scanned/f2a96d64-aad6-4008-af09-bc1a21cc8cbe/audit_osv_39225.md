# [M] NanoMQ: QUIC Dialer Close Type Confusion

## Summary
Severity: Medium
Advisory: CVE-2026-44640
Aliases: GHSA-9fgw-v323-jmjj
CVSS: 4.5 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2026-05-29
Source: https://osv.dev/vulnerability/CVE-2026-44640
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. Prior to 0.24.14, aio->prov_data is stored as nni_quic_conn* during dialing, but read as ex_quic_conn* during dialer close. This type confusion causes invalid object interpretation and leads to close-path hang/crash behavior. This vulnerability is fixed in 0.24.14.

## References
- https://github.com/nanomq/nanomq/releases/tag/0.24.14
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44640.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-9fgw-v323-jmjj
- https://nvd.nist.gov/vuln/detail/CVE-2026-44640
