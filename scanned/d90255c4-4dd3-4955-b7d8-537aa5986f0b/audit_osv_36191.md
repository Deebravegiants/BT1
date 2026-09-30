# [H] MQTT v5 Variable Byte Integer parsing out-of-bounds: get_var_integer()

## Summary
Severity: High
Advisory: CVE-2026-21888
Aliases: GHSA-cggc-6m7w-j7x5
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-21888
Type: osv

## Details
NanoMQ MQTT Broker (NanoMQ) is an all-around Edge Messaging Platform. MQTT v5 Variable Byte Integer parsing out-of-bounds: get_var_integer() accepts 5-byte varints without bounds checks; reliably triggers OOB read / crash when built with ASan. This affects 0.24.6 and earlier.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21888.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-cggc-6m7w-j7x5
- https://nvd.nist.gov/vuln/detail/CVE-2026-21888
- https://github.com/nanomq/nanomq/issues/2192
