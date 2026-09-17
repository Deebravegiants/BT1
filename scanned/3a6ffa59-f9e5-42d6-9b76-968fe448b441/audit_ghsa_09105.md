# [M] GoBGP has an Integer Underflow Issue

## Summary
Severity: Medium
Advisory: GHSA-hj4w-qr9j-c4cf
CVE: CVE-2026-7736
CWE: CWE-191
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-hj4w-qr9j-c4cf
Type: github-advisory

## Affected
- Go: `github.com/osrg/gobgp/v4` — affected >=0 <4.4.0

## Details
A vulnerability was determined in osrg GoBGP up to 4.3.0. Affected by this vulnerability is the function parseRibEntry of the file pkg/packet/mrt/mrt.go. Executing a manipulation can lead to integer underflow. It is possible to launch the attack remotely. Upgrading to version 4.4.0 addresses this issue. This patch is called 76d911046344a3923cbe573364197aa081944592. It is suggested to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7736
- https://github.com/osrg/gobgp/commit/76d911046344a3923cbe573364197aa081944592
- https://github.com/osrg/gobgp
- https://github.com/osrg/gobgp/releases/tag/v4.4.0
- https://vuldb.com/submit/807604
- https://vuldb.com/vuln/360911
- https://vuldb.com/vuln/360911/cti
