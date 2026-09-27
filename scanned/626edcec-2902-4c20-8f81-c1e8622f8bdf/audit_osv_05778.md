# [C] Arbitrary Code Execution in Grafana Image Renderer Plugin

## Summary
Severity: Critical
Advisory: BIT-grafana-image-renderer-2025-11539
Aliases: CVE-2025-11539
Ecosystem: Bitnami
Published: 2025-10-11
Source: https://osv.dev/vulnerability/BIT-grafana-image-renderer-2025-11539
Type: osv

## Affected
- Bitnami: `grafana-image-renderer` — affected >=1.0.0 <4.0.17

## Details
Grafana Image Renderer is vulnerable to remote code execution due to an arbitrary file write vulnerability. This is due to the fact that the /render/csv endpoint lacked validation of the filePath parameter that allowed an attacker to save a shared object to an arbitrary location that is then loaded by the Chromium process.

Instances are vulnerable if:

1. The default token ("authToken") is not changed, or is known to the attacker.
2. The attacker can reach the image renderer endpoint.
This issue affects grafana-image-renderer: from 1.0.0 through 4.0.16.

## References
- https://github.com/grafana/grafana-image-renderer/releases/tag/v4.0.17
- https://grafana.com/security/security-advisories/cve-2025-11539/
- https://nvd.nist.gov/vuln/detail/CVE-2025-11539
