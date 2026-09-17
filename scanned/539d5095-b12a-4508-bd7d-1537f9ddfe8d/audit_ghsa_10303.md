# [M] PicoClaw has an Injection issue in its Web Launcher Management Plane component

## Summary
Severity: Medium
Advisory: GHSA-6r3x-h84w-fhxx
CVE: CVE-2026-6987
CWE: CWE-74
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-25
Source: https://github.com/advisories/GHSA-6r3x-h84w-fhxx
Type: github-advisory

## Affected
- Go: `github.com/sipeed/picoclaw` — affected >=0

## Details
A vulnerability was detected in PicoClaw up to 0.2.4. Impacted is an unknown function of the file /api/gateway/restart of the component Web Launcher Management Plane. Performing a manipulation results in command injection. It is possible to initiate the attack remotely. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-6987
- https://github.com/sipeed/picoclaw/issues/2307
- https://github.com/sipeed/picoclaw
- https://vuldb.com/submit/796336
- https://vuldb.com/vuln/359530
- https://vuldb.com/vuln/359530/cti
