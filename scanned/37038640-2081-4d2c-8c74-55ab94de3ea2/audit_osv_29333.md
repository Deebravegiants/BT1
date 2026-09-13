# [M] FOG Weak file permissions

## Summary
Severity: Medium
Advisory: CVE-2024-41954
Aliases: GHSA-pcqm-h8cx-282c
CVSS: 5.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/CVE-2024-41954
Type: osv

## Details
FOG is a cloning/imaging/rescue suite/inventory management system. The application stores plaintext service account credentials in the "/opt/fog/.fogsettings" file. This file is by default readable by all users on the host. By exploiting these credentials, a malicious user could create new accounts for the web application and much more. The vulnerability is fixed in 1.5.10.41.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41954.json
- https://github.com/FOGProject/fogproject/security/advisories/GHSA-pcqm-h8cx-282c
- https://nvd.nist.gov/vuln/detail/CVE-2024-41954
- https://github.com/FOGProject/fogproject/commit/97ed6d51608e52fc087ca1d2f03d6b8df612fc90
