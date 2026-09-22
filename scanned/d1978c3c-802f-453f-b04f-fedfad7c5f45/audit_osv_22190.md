# [H] Arbitrary file access in the Galaxy data analysis platform

## Summary
Severity: High
Advisory: CVE-2022-23470
Aliases: GHSA-grjf-2ghx-q77x
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-12-06
Source: https://osv.dev/vulnerability/CVE-2022-23470
Type: osv

## Details
Galaxy is an open-source platform for data analysis. An arbitrary file read exists in Galaxy 22.01 and Galaxy 22.05 due to the switch to Gunicorn, which can be used to read any file accessible to the operating system user under which Galaxy is running. This vulnerability affects Galaxy 22.01 and higher, after the switch to gunicorn, which serve static contents directly.  Additionally, the vulnerability is mitigated when using Nginx or Apache to serve /static/* contents, instead of Galaxy's internal middleware. This issue has been patched in commit `e5e6bda4f` and will be included in future releases. Users are advised to manually patch their installations. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23470.json
- https://github.com/galaxyproject/galaxy/security/advisories/GHSA-grjf-2ghx-q77x
- https://nvd.nist.gov/vuln/detail/CVE-2022-23470
- https://github.com/galaxyproject/galaxy/commit/e5e6bda4f014f807ca77ee0cf6af777a55918346
