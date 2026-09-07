# [H] NLnet Labs Routinator has Reachable Assertion vulnerability

## Summary
Severity: High
Advisory: GHSA-m4vx-ccrf-w399
CVE: CVE-2022-3029
CWE: CWE-617
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-14
Source: https://github.com/advisories/GHSA-m4vx-ccrf-w399
Type: github-advisory

## Affected
- crates.io: `routinator` — affected >=0.9.0 <0.11.3

## Details
In NLnet Labs Routinator 0.9.0 up to and including 0.11.2, due to a mistake in error handling, data in RRDP snapshot and delta files which are not correctly base 64 encoded are treated as a fatal error and causes Routinator to exit. Worst case impact of this vulnerability is denial of service for the RPKI data that Routinator provides to routers. This may stop your network from validating route origins based on RPKI data. This vulnerability does not allow an attacker to manipulate RPKI data.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-3029
- https://github.com/NLnetLabs/routinator/pull/781/commits/c2e2476f28f09ea5ffb22d172d84fb4f8384d496
- https://github.com/NLnetLabs/routinator
- https://github.com/NLnetLabs/routinator/releases/tag/v0.11.3
- https://www.nlnetlabs.nl/downloads/routinator/CVE-2022-3029.txt
