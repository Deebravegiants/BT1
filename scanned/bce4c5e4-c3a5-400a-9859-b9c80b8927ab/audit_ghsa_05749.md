# [M] Ghost has SSRF via External Media Inliner

## Summary
Severity: Medium
Advisory: GHSA-vmc4-9828-r48r
CVE: CVE-2026-22597
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-vmc4-9828-r48r
Type: github-advisory

## Affected
- npm: `ghost` — affected >=6.0.0 <6.11.0
- npm: `ghost` — affected >=5.105.0 <5.130.6

## Details
### Impact
A vulnerability in Ghost’s media inliner mechanism allows staff users in possession of a valid authentication token for the Ghost Admin API to exfiltrate data from internal systems via SSRF.

### Vulnerable versions
This vulnerability is present in Ghost v5.38.0 to v5.130.5 to and Ghost v6.0.0 to v6.10.3.

### Patches
v5.130.6 and v6.11.0 contain a fix for this issue.

### References
Ghost thanks Sho Odagiri of GMO Cybersecurity by Ierae, Inc. for discovering and disclosing this vulnerability responsibly.

### For more information
If there are any questions or comments about this advisory, email Ghost at [security@ghost.org](mailto:security@ghost.org).

## References
- https://github.com/TryGhost/Ghost/security/advisories/GHSA-vmc4-9828-r48r
- https://nvd.nist.gov/vuln/detail/CVE-2026-22597
- https://github.com/TryGhost/Ghost/commit/15d49131ff4aac3aca8642501c793f01f2bfcbb9
- https://github.com/TryGhost/Ghost/commit/93add549ccf079d8e28bdb724fbb71a76942ff51
- https://github.com/TryGhost/Ghost
