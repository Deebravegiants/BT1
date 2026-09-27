# [M] CVE-2021-39246

## Summary
Severity: Medium
Advisory: CVE-2021-39246
CVSS: 6.1 (CVSS:3.1/AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-09-24
Source: https://osv.dev/vulnerability/CVE-2021-39246
Type: osv

## Details
Tor Browser through 10.5.6 and 11.x through 11.0a4 allows a correlation attack that can compromise the privacy of visits to v2 onion addresses. Exact timestamps of these onion-service visits are logged locally, and an attacker might be able to compare them to timestamp data collected by the destination server (or collected by a rogue site within the Tor network).

## References
- https://gitlab.torproject.org/tpo/core/tor/-/merge_requests/434
- https://www.privacyaffairs.com/cve-2021-39246-tor-vulnerability
- https://gitlab.torproject.org/tpo/core/tor/-/commit/80c404c4b79f3bcba3fc4585d4c62a62a04f3ed9
- https://github.com/sickcodes/security/blob/master/advisories/SICK-2021-111.md
- https://sick.codes/sick-2021-111
