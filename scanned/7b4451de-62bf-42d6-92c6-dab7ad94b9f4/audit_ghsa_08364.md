# [M] Velocidex Velociraptor has an off-by-one error

## Summary
Severity: Medium
Advisory: GHSA-6cmp-qv2f-x97x
CVE: CVE-2026-7572
CWE: CWE-193
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-6cmp-qv2f-x97x
Type: github-advisory

## Affected
- Go: `www.velocidex.com/golang/velociraptor` — affected >=0 <0.76.5

## Details
An off-by-one error (CWE-193) in the ConsumeUnit16Array and ConsumeUnit64Array functions in Velocidex Velociraptor before version 0.76.5 on Windows and Linux allows a local attacker to cause a Denial of Service (DoS) via a process crash by providing a specially crafted .evtx file to the parse_evtx VQL plugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7572
- https://docs.velociraptor.app/announcements/advisories/cve-2026-7572
- https://github.com/Velocidex/velociraptor
