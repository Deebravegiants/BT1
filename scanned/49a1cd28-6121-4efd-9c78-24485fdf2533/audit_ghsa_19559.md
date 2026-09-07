# [M] Rasa Pro Missing Authentication For Voice Connector APIs

## Summary
Severity: Medium
Advisory: GHSA-7xq5-54jp-2mfg
CVE: CVE-2025-32377
CWE: CWE-306
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-04-17
Source: https://github.com/advisories/GHSA-7xq5-54jp-2mfg
Type: github-advisory

## Affected
- PyPI: `rasa-pro` — affected >=3.12.0 <3.12.6
- PyPI: `rasa-pro` — affected >=3.11.0 <3.11.7
- PyPI: `rasa-pro` — affected >=3.10.0 <3.10.19
- PyPI: `rasa-pro` — affected >=0 <3.9.20

## Details
## Vulnerability
A vulnerability has been identified in Rasa Pro where voice connectors in Rasa Pro do not properly implement authentication even when a token is configured in the `credentials.yml` file. This could allow an attacker to submit voice data to the Rasa Pro assistant from an unauthenticated source.

This impacts the following connectors:

- `audiocodes_stream`
- `genesys`
- `jambonz`

As part of our investigation to resolve this issue, we have also performed a security review of our other voice channel connectors:

- `browser_audio`: Does not support authentication. This is a development channel not intended for production use.
- `twilio_media_streams`, `twilio_voice` and `jambonz`: Authentication is currently not supported by these channels, but our investigation has found a way for us to enable it for these voice channel connectors in a future Rasa Pro release.

## Fix
The issue has been resolved for `audiocodes`, `audiocodes_stream`, and `genesys` connectors. Fixed versions of Rasa Pro have been released for `3.9.20`, `3.10.19`, `3.11.7` and `3.12.6`. Please update to a fixed release.

If you are using one of the affected connectors, we strongly recommend upgrading to a fixed version. For connectors where authentication is not supported (e.g., Twilio), we suggest taking extra caution and considering other compensating controls if applicable.

## References
- https://github.com/RasaHQ/rasa-pro-security-advisories/security/advisories/GHSA-7xq5-54jp-2mfg
- https://github.com/RasaHQ/security-advisories/security/advisories/GHSA-7xq5-54jp-2mfg
- https://nvd.nist.gov/vuln/detail/CVE-2025-32377
