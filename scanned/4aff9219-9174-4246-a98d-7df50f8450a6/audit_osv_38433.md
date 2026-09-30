# [C] OpenCTI affected by RCE via notifier template

## Summary
Severity: Critical
Advisory: CVE-2026-39980
Aliases: GHSA-jv9r-jw2f-rhrf, PYSEC-2026-2265
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-04-09
Source: https://osv.dev/vulnerability/CVE-2026-39980
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. Prior to 6.9.5, the safeEjs.ts file does not properly sanitize EJS templates. Users with the Manage customization capability can run arbitrary JavaScript in the context of the OpenCTI platform process during notifier template execution. This vulnerability is fixed in 6.9.5.

## References
- https://github.com/OpenCTI-Platform/opencti/releases/tag/6.9.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/39xxx/CVE-2026-39980.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-jv9r-jw2f-rhrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-39980
