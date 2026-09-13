# [M] Path traversal in metersphere

## Summary
Severity: Medium
Advisory: CVE-2023-37461
Aliases: GHSA-xfr9-jgfp-fx3v
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2023-07-17
Source: https://osv.dev/vulnerability/CVE-2023-37461
Type: osv

## Details
Metersphere is an opensource testing framework. Files uploaded to Metersphere may define a `belongType` value with a relative path like `../../../../` which may cause metersphere to attempt to overwrite an existing file in the defined location or to create a new file. Attackers would be limited to overwriting files that the metersphere process has access to. This issue has been addressed in version 2.10.3. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37461.json
- https://github.com/metersphere/metersphere/security/advisories/GHSA-xfr9-jgfp-fx3v
- https://nvd.nist.gov/vuln/detail/CVE-2023-37461
