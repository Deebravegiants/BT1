# [H] OpenEMR has SQL Injection Vulnerability

## Summary
Severity: High
Advisory: CVE-2026-25746
Aliases: GHSA-78r7-g65p-gpw3
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25746
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Versions prior to 8.0.0 contain a SQL injection vulnerability in prescription that can be exploited by authenticated attackers. The vulnerability exists due to insufficient input validation in the prescription listing functionality. Version 8.0.0 fixes the vulnerability.

## References
- https://github.com/openemr/openemr/blob/2b46e594b9dd665fb7f16c913ca07f5c6d54412b/library/classes/Controller.class.php#L77
- https://github.com/openemr/openemr/blob/9fa8db9f12d0b70985195b11b90f2dc564bd3b24/controller.php#L6
- https://github.com/openemr/openemr/blob/9fa8db9f12d0b70985195b11b90f2dc564bd3b24/controllers/C_Prescription.class.php#L180
- https://github.com/openemr/openemr/blob/9fa8db9f12d0b70985195b11b90f2dc564bd3b24/library/classes/Prescription.class.php#L1148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25746.json
- https://github.com/openemr/openemr/security/advisories/GHSA-78r7-g65p-gpw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-25746
- https://github.com/openemr/openemr/commit/e230d3ef46425ffc96a37dc6369428aa37c88554
- https://github.com/ChrisSub08/CVE-2026-25746_SqlInjectionVulnerabilityOpenEMR7.0.4
