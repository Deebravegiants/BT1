# [M] Wazuh: CRLF Log Injection via Unsanitized Basic-Auth Username

## Summary
Severity: Medium
Advisory: CVE-2026-44256
Aliases: GHSA-c3m6-fp2h-wmr4
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-44256
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.4.0 until 4.14.6 and 5.0.0-beta2, api/api/middlewares.py decodes the Basic authentication username before credential validation and passes it to the access logger without neutralizing control characters. api/api/alogging.py interpolates that value into the plain-text API log. An unauthenticated attacker can include carriage returns or line feeds in the username to forge entries, obscure activity, or poison systems that consume the plain-text audit log. The JSON log format is not affected because JSON serialization escapes these characters. This issue is fixed in versions 4.14.6 and 5.0.0-beta2.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44256.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-c3m6-fp2h-wmr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-44256
- https://github.com/wazuh/wazuh/commit/cddf3fd16b0f945b28eb9c27714de3cc344e0926
- https://github.com/wazuh/wazuh/pull/35866
