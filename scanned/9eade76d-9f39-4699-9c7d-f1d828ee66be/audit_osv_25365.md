# [H] CVE-2023-34488

## Summary
Severity: High
Advisory: CVE-2023-34488
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-12
Source: https://osv.dev/vulnerability/CVE-2023-34488
Type: osv

## Details
NanoMQ 0.17.5 has a one-byte heap-based buffer over-read in the conn_handler function of mqtt_parser.c when it processes malformed messages.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34488.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-34488
- https://github.com/emqx/nanomq/issues/1181
