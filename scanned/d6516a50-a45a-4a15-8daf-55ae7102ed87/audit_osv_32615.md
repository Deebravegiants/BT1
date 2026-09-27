# [M] OpenEMR doesn't log password administration properly

## Summary
Severity: Medium
Advisory: CVE-2025-32967
Aliases: GHSA-7qj6-jxfc-xw4v
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-05-23
Source: https://osv.dev/vulnerability/CVE-2025-32967
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. A logging oversight in versions prior to 7.0.3.4 allows password change events to go unrecorded on the client-side log viewer, preventing administrators from auditing critical actions. This weakens traceability and opens the system to undetectable misuse by insiders or attackers. Version 7.0.3.4 contains a patch for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32967.json
- https://github.com/openemr/openemr/security/advisories/GHSA-7qj6-jxfc-xw4v
- https://nvd.nist.gov/vuln/detail/CVE-2025-32967
