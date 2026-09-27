# [C] FUXA Unauthenticated Exposure of Plaintext Database Credentials

## Summary
Severity: Critical
Advisory: GHSA-c5gq-4h56-4mmx
CVE: CVE-2026-25751
CWE: CWE-306, CWE-312
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-05
Source: https://github.com/advisories/GHSA-c5gq-4h56-4mmx
Type: github-advisory

## Affected
- npm: `fuxa-server` — affected >=0 <1.2.10

## Details
### Description
An information disclosure vulnerability in FUXA allows an unauthenticated, remote attacker to retrieve sensitive administrative database credentials. This affects FUXA through version 1.2.9. This issue has been patched in FUXA version 1.2.10.

### Impact
This affects all deployments, including those with `runtime.settings.secureEnabled` set to `true`.

Exploitation allows an unauthenticated, remote attacker to obtain the full system configuration, including administrative credentials for the InfluxDB database. Possession of these credentials may allow an attacker to authenticate directly to the database service, enabling them to read, modify, or delete all historical process data, or perform a Denial of Service by corrupting the database.

### Patches
This issue has been patched in FUXA version 1.2.10. Users are strongly encouraged to update to the latest available release.

## References
- https://github.com/frangoteam/FUXA/security/advisories/GHSA-c5gq-4h56-4mmx
- https://nvd.nist.gov/vuln/detail/CVE-2026-25751
- https://github.com/frangoteam/FUXA/commit/c6c4cba1a62545e8e3ae0f43b2269e61209fbee8
- https://github.com/frangoteam/FUXA
- https://github.com/frangoteam/FUXA/releases/tag/v1.2.10
