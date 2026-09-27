# [M] Global Settings Publication Exposes Sensitive Configuration to Any Authenticated User in Titra

## Summary
Severity: Medium
Advisory: CVE-2026-42092
Aliases: GHSA-4h9p-49hg-vppw
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/CVE-2026-42092
Type: osv

## Details
titra is an open source time tracking project. In version 0.99.52, the globalsettings Meteor publication returns all global settings without any admin or role check. Any authenticated user can subscribe via DDP and receive sensitive configuration fields such as google_secret, openai_apikey, and google_clientid. At time of publication no public patch is available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42092.json
- https://github.com/titraio/titra/security/advisories/GHSA-4h9p-49hg-vppw
- https://nvd.nist.gov/vuln/detail/CVE-2026-42092
