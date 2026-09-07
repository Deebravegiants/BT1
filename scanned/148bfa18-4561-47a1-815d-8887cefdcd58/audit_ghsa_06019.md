# [M] Ghost: Mobiledoc image-size fetch SSRF

## Summary
Severity: Medium
Advisory: GHSA-g366-23fw-ggp6
CVE: CVE-2026-53946
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-04
Source: https://github.com/advisories/GHSA-g366-23fw-ggp6
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.19.4 <6.21.2

## Details
### Impact

When re-rendering posts, Ghost would refetch missing image dimensions by issuing an outbound HTTP request to the URL stored on an image card — without restricting that URL to trusted image hosts. An authenticated staff user able to create or edit posts could therefore point an image card at an attacker-chosen host and cause the Ghost server to request it on their behalf, including hosts on internal networks or cloud instance metadata endpoints that would not normally be reachable from the public internet.

### Vulnerable versions

This vulnerability is present in Ghost from v6.19.3 up to v6.21.0.

### Patches

v6.21.1 contains a fix for this issue.

### How to update

For self-hosters using Docker, find [Docker's official Ghost image here](https://hub.docker.com/_/ghost). Updating a Docker-based Ghost instance [is documented here](https://docs.ghost.org/install/docker#updating-ghost). 

If your Ghost is a Ghost-CLI install see our documentation on [updating it to the latest version here](https://docs.ghost.org/update). 

### For more information

If you have any questions or comments about this advisory, email us at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-g366-23fw-ggp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-53946
- https://github.com/TryGhost/Ghost/pull/26753
- https://github.com/TryGhost/Ghost/commit/ba692df7f27162d0440d57487f16c530416a8eb2
- https://github.com/TryGhost/Ghost
- https://github.com/TryGhost/Ghost/releases/tag/v6.21.1
