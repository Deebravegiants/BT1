# [M] BigBlueButton's missing authorization allows viewer to inject/overwrite captions

## Summary
Severity: Medium
Advisory: CVE-2026-41127
Aliases: GHSA-q387-2q28-mg33
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41127
Type: osv

## Details
BigBlueButton is an open-source virtual classroom. Versions prior to 3.0.24 have a missing authorization that allows viewers to inject/overwrite captions Version 3.0.24 tightened the permissions on who is able to submit captions. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41127.json
- https://github.com/bigbluebutton/bigbluebutton/security/advisories/GHSA-q387-2q28-mg33
- https://nvd.nist.gov/vuln/detail/CVE-2026-41127
