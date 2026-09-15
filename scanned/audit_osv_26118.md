# [M] Information Disclosure Vulnerability in Journalpump

## Summary
Severity: Medium
Advisory: CVE-2023-51390
Aliases: GHSA-738v-v386-8r6g
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-12-20
Source: https://osv.dev/vulnerability/CVE-2023-51390
Type: osv

## Details
journalpump is a daemon that takes log messages from journald and pumps them to a given output. A logging vulnerability was found in journalpump which logs out the configuration of a service integration in plaintext to the supplied logging pipeline, including credential information contained in the configuration if any. The problem has been patched in journalpump 2.5.0.

## References
- https://github.com/Aiven-Open/journalpump/security/advisories/GHSA-738v-v386-8r6g
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/51xxx/CVE-2023-51390.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-51390
- https://github.com/Aiven-Open/journalpump/commit/390e69bc909ba16ad5f7b577010b4afc303361da
