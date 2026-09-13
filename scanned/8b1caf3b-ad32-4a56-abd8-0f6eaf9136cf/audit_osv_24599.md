# [M] Metabase subject to Exposure of Sensitive Information to an Unauthorized Actor

## Summary
Severity: Medium
Advisory: CVE-2023-23628
Aliases: GHSA-492f-qxr3-9rrv
CVSS: 5.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-01-28
Source: https://osv.dev/vulnerability/CVE-2023-23628
Type: osv

## Details
Metabase is an open source data analytics platform. Affected versions are subject to Exposure of Sensitive Information to an Unauthorized Actor. Sandboxed users shouldn't be able to view data about other Metabase users anywhere in the Metabase application. However, when a sandbox user views the settings for a dashboard subscription, and another user has added users to that subscription, the sandboxed user is able to view the list of recipients for that subscription. This issue is patched in versions 0.43.7.1, 1.43.7.1, 0.44.6.1, 1.44.6.1, 0.45.2.1, and 1.45.2.1. There are no workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23628.json
- https://github.com/metabase/metabase/security/advisories/GHSA-492f-qxr3-9rrv
- https://nvd.nist.gov/vuln/detail/CVE-2023-23628
