# [M] Graylog's Authenticated HTTP inputs ingest message even if Authorization header is missing or has wrong value

## Summary
Severity: Medium
Advisory: GHSA-q7g5-jq6p-6wvx
CVE: CVE-2025-30373
CWE: CWE-285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2025-04-07
Source: https://github.com/advisories/GHSA-q7g5-jq6p-6wvx
Type: github-advisory

## Affected
- Maven: `org.graylog2:graylog2-server` — affected >=6.1.0 <6.1.9

## Details
### Impact
Starting with 6.1, HTTP Inputs can be configured to check if a specified header is present and has a specified value to authenticate HTTP-based ingestion. Unfortunately, even though in cases of a missing header or a wrong value the correct HTTP response (401) is returned, the message will be ingested nonetheless.

### Patches

### Workarounds
Disabling http-based inputs and allow only authenticated pull-based inputs.

Analysis provided by Fabian Yamaguchi - Whirly Labs (Pty) Ltd

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-q7g5-jq6p-6wvx
- https://nvd.nist.gov/vuln/detail/CVE-2025-30373
- https://github.com/Graylog2/graylog2-server/commit/31bc13d3cd6f550ec83473d0f8666cd3ebf50f10
- https://github.com/Graylog2/graylog2-server
