# [H] Recce server has unauthenticated SQL execution that allows local file read/write through DuckDB

## Summary
Severity: High
Advisory: GHSA-rh62-j648-g5qc
CVE: CVE-2026-49360
CWE: CWE-73
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:L/SC:L/SI:H/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-rh62-j648-g5qc
Type: github-advisory

## Affected
- PyPI: `recce` — affected >=0 <1.50.0

## Details
### Impact
Recce OSS server deployments that expose the server to an untrusted network without authentication are vulnerable to unauthenticated SQL execution through the query run API.

When Recce is configured with a DuckDB-backed project, an attacker can use DuckDB filesystem primitives to read and write files accessible to the Recce server process. The impact depends on how Recce is deployed, but may include disclosure of local files, tampering with Recce/dbt artifacts, modification of browser-served static files leading to stored XSS, and modification of application files if those paths are writable. If Recce is run as root, file access occurs with root privileges inside that host or container.

### Patches
This issue has been patched in Recce `v1.50.0`. Users should upgrade to Recce `v1.50.0` or later.

The patch restricts unsafe file read/write behavior for DuckDB-backed query execution and hardens the affected query path. Other warehouse adapters have also been reviewed for similar exposure.

### Credits
Thanks to Sitampan ([@hxcbtc](https://x.com/hxcbtc)) for responsibly reporting this issue.

### Workarounds
Users who cannot upgrade immediately should avoid exposing `recce server` to the public internet or any untrusted network.

Recommended mitigations include enabling authentication or placing Recce behind an authenticated reverse proxy/VPN, running Recce as a non-root user, using a read-only application filesystem where possible, and ensuring that sensitive files or credentials are not available to the Recce process.

## References
- https://github.com/DataRecce/recce/security/advisories/GHSA-rh62-j648-g5qc
- https://github.com/DataRecce/recce
- https://github.com/DataRecce/recce/releases/tag/v1.50.0
