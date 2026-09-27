# [M] short-video-maker has a path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-935g-9rq5-q95c
CVE: CVE-2026-8115
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-935g-9rq5-q95c
Type: github-advisory

## Affected
- npm: `short-video-maker` — affected >=0

## Details
A security flaw has been discovered in gyoridavid short-video-maker up to 1.3.4. This affects an unknown part of the file src/server/routers/rest.ts of the component REST API. The manipulation of the argument req.params.tmpFile results in path traversal. The attack can be launched remotely. The exploit has been released to the public and may be used for attacks. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-8115
- https://github.com/gyoridavid/short-video-maker/issues/73
- https://github.com/gyoridavid/short-video-maker
- https://vuldb.com/submit/808258
- https://vuldb.com/vuln/361903
- https://vuldb.com/vuln/361903/cti
