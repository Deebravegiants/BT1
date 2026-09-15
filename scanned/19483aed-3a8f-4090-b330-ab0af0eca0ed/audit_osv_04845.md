# [H] BIT-fluent-bit-2024-50608

## Summary
Severity: High
Advisory: BIT-fluent-bit-2024-50608
Aliases: CVE-2024-50608
Ecosystem: Bitnami
Published: 2025-04-23
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2024-50608
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=3.1.9 <3.1.10

## Details
An issue was discovered in Fluent Bit 3.1.9. When the Prometheus Remote Write input plugin is running and listening on an IP address and port, one can send a packet with Content-Length: 0 and it crashes the server. Improper handling of the case when Content-Length is 0 allows a user (with access to the endpoint) to perform a remote Denial of service attack. The crash happens because of a NULL pointer dereference when 0 (from the Content-Length) is passed to the function cfl_sds_len, which in turn tries to cast a NULL pointer into struct cfl_sds. This is related to process_payload_metrics_ng() at prom_rw_prot.c.

## References
- https://fluentbit.io/announcements/
- https://github.com/fluent/fluent-bit/releases
- https://nvd.nist.gov/vuln/detail/CVE-2024-50608
- https://www.ebryx.com/blogs/exploring-cve-2024-50608-and-cve-2024-50609
