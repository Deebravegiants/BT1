# [M] daphne: Unauthenticated attackers can cause excessive memory consumption by sending arbitrarily large WebSocket messages/frames

## Summary
Severity: Medium
Advisory: GHSA-rrc9-mx66-ffcm
CVE: CVE-2026-44545
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-rrc9-mx66-ffcm
Type: github-advisory

## Affected
- PyPI: `daphne` — affected >=0 <4.2.2

## Details
daphne before 4.2.2 did not pass maxFramePayloadSize or maxMessagePayloadSize to Autobahn's WebSocketServerFactory. Because Autobahn defaults both values to 0 (unlimited), an unauthenticated remote attacker could send arbitrarily large WebSocket messages or frames, causing excessive memory consumption and a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44545
- https://github.com/django/daphne
- https://github.com/django/daphne/blob/main/CHANGELOG.txt
- https://github.com/pypa/advisory-database/tree/main/vulns/daphne/PYSEC-2026-213.yaml
