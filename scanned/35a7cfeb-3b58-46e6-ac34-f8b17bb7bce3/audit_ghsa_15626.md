# [C] TorrentPier Deserialization of Untrusted Data vulnerability

## Summary
Severity: Critical
Advisory: GHSA-fg86-4c2r-7wxw
CVE: CVE-2024-40624
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-15
Source: https://github.com/advisories/GHSA-fg86-4c2r-7wxw
Type: github-advisory

## Affected
- Packagist: `torrentpier/torrentpier` — affected >=0 <2.4.4

## Details
### Summary

In `torrentpier/library/includes/functions.php`, `get_tracks()` uses the unsafe native PHP serialization format to deserialize user-controlled cookies:

https://github.com/torrentpier/torrentpier/blob/84f6c9f4a081d9ffff4c233098758280304bf50f/library/includes/functions.php#L41-L60

### PoC

One can use [`phpggc`](https://github.com/ambionics/phpggc/) and the chain `Guzzle/FW1` to write PHP code to an arbitrary file, and execute commands on the system. For instance, the cookie `bb_t` will be deserialized when browsing to `viewforum.php`.

## References
- https://github.com/torrentpier/torrentpier/security/advisories/GHSA-fg86-4c2r-7wxw
- https://nvd.nist.gov/vuln/detail/CVE-2024-40624
- https://github.com/torrentpier/torrentpier/commit/ed37e6e522f345f2b46147c6f53c1ab6dec1db9e
- https://github.com/torrentpier/torrentpier
- https://github.com/torrentpier/torrentpier/blob/84f6c9f4a081d9ffff4c233098758280304bf50f/library/includes/functions.php#L41-L60
