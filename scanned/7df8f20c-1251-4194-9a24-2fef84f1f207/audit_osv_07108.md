# [H] Apache NiFi: Uncontrolled Resource Consumption through Decompression of HTTP Requests

## Summary
Severity: High
Advisory: BIT-nifi-2026-68981
Aliases: CVE-2026-68981
Ecosystem: Bitnami
Published: 2026-08-17
Source: https://osv.dev/vulnerability/BIT-nifi-2026-68981
Type: osv

## Affected
- Bitnami: `nifi` — affected >=1.5.0 <2.11.0

## Details
Apache NiFi 1.5.0 through 2.10.0 support gzip-encoded HTTP requests for the application REST API using a Jersey encoding filter. The framework enforced a configurable maximum request size on the compressed payload rather than the decompressed output, allowing a malicious client to send crafted requests that could consume excessive amounts of memory. Upgrading to Apache NiFi 2.11.0 is the recommended mitigation, which relocates response compression to Jetty Server and disables decompression of gzip-encoded HTTP requests.

## References
- http://www.openwall.com/lists/oss-security/2026/08/03/13
- https://lists.apache.org/thread/vxrqn7poyf1wx6gdy7c0dxqfqkctjngg
- https://nvd.nist.gov/vuln/detail/CVE-2026-68981
