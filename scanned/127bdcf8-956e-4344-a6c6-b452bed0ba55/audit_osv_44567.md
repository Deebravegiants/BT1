# [C] Windows ML CLI: CORS misconfig enables localhost RCE

## Summary
Severity: Critical
Advisory: CVE-2026-84452
Aliases: GHSA-96p9-rh4f-92cf, PYSEC-2026-3944
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-02
Source: https://osv.dev/vulnerability/CVE-2026-84452
Type: osv

## Details
Windows ML CLI is a command line tool for building portable, performant, and high-quality AI models for Windows ML. Prior to 0.4.0, the src/winml/modelkit/serve/cli_api.py component exposes WinML CLI commands through a localhost HTTP API without authentication and configures the allow_origins setting as a wildcard in both src/winml/modelkit/serve/cli_api.py and src/winml/modelkit/serve/app.py. A malicious website loaded by a user can send cross-origin requests to /v1/cli/build or /v1/cli/config and set the trust_remote_code parameter to true, which is converted to the --trust-remote-code command-line flag without validation. This reaches AutoConfig.from_pretrained with trust_remote_code=True in src/winml/modelkit/loader/_autoconfig.py and imports Python code from an attacker-controlled model repository, resulting in arbitrary code execution as the server user. This issue is fixed in version 0.4.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/84xxx/CVE-2026-84452.json
- https://github.com/microsoft/winml-cli/security/advisories/GHSA-96p9-rh4f-92cf
- https://nvd.nist.gov/vuln/detail/CVE-2026-84452
- https://github.com/microsoft/winml-cli/commit/f4073e0ef4700a25b623487e7e45c421ca0b9993
- https://github.com/microsoft/winml-cli/pull/1321
