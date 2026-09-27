# [H] OpenCTI: Authorization Bypass via `synchronized-upsert` HTTP Header Injection

## Summary
Severity: High
Advisory: CVE-2026-35210
Aliases: GHSA-36fr-4m54-94mj, PYSEC-2026-3445
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-35210
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. Prior to 7.260326.0, an authorization bypass vulnerability in OpenCTI allows any authenticated user with KNOWLEDGE_KNUPDATE permission to bypass Confidence Level validation and Object Marking restrictions by injecting the synchronized-upsert: true HTTP header, enabling attackers to downgrade confidence levels, remove security markings such as TLP:RED, manipulate relationships, and affect STIX object types including Indicators, ThreatActors, Malware, and Reports. This issue is fixed in version 7.260326.0.

## References
- https://github.com/OpenCTI-Platform/opencti/releases/tag/7.260326.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/35xxx/CVE-2026-35210.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-36fr-4m54-94mj
- https://nvd.nist.gov/vuln/detail/CVE-2026-35210
- https://github.com/OpenCTI-Platform/opencti/commit/134531ddf5ecf741006b7f0870b7c36711b96540
- https://github.com/OpenCTI-Platform/opencti/pull/14243
