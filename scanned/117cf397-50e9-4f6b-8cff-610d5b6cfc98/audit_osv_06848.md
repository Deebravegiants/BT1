# [H] ModSecurity: Multipart form-data parser silently strips embedded line breaks from form-field values, enabling request-body inspection bypass

## Summary
Severity: High
Advisory: BIT-modsecurity-2026-52747
Aliases: CVE-2026-52747, GHSA-rcw9-2f5r-7p88
Ecosystem: Bitnami
Published: 2026-07-15
Source: https://osv.dev/vulnerability/BIT-modsecurity-2026-52747
Type: osv

## Affected
- Bitnami: `modsecurity` — affected >=0 <3.0.16

## Details
ModSecurity is an open source, cross platform web application firewall (WAF) engine for Apache, IIS and Nginx. Prior to 3.0.16, the multipart/form-data request body parser in libmodsecurity silently removes embedded line breaks from non-file form-field values before exporting them to ARGS and ARGS_POST because src/request_body_processor/multipart.cc overwrites reserved bytes in m_reserve instead of appending the current buffer. This creates a parser differential between ModSecurity and backend applications that preserve line breaks in form fields, allowing rules that inspect ARGS or ARGS_POST to miss payloads whose dangerous syntax depends on a line break. This issue is fixed in version 3.0.16.

## References
- https://github.com/owasp-modsecurity/ModSecurity/commit/875504c2758169c41be1ad2f0cc64d896b7815d7
- https://github.com/owasp-modsecurity/ModSecurity/releases/tag/v3.0.16
- https://github.com/owasp-modsecurity/ModSecurity/security/advisories/GHSA-rcw9-2f5r-7p88
- https://nvd.nist.gov/vuln/detail/CVE-2026-52747
