# [H] BIT-nifi-2020-1942

## Summary
Severity: High
Advisory: BIT-nifi-2020-1942
Aliases: CVE-2020-1942, GHSA-7q8g-gpfp-v8gx
Ecosystem: Bitnami
Published: 2025-09-12
Source: https://osv.dev/vulnerability/BIT-nifi-2020-1942
Type: osv

## Affected
- Bitnami: `nifi` — affected >=0.0.1

## Details
In Apache NiFi 0.0.1 to 1.11.0, the flow fingerprint factory generated flow fingerprints which included sensitive property descriptor values. In the event a node attempted to join a cluster and the cluster flow was not inheritable, the flow fingerprint of both the cluster and local flow was printed, potentially containing sensitive values in plaintext.

## References
- https://nifi.apache.org/security.html#CVE-2020-1942
- https://nvd.nist.gov/vuln/detail/CVE-2020-1942
