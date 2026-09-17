# [H] Deserialization Vulnerability by yaml config input in super-xray

## Summary
Severity: High
Advisory: CVE-2022-41958
Aliases: GHSA-39pv-4vmj-c4fr
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-11-25
Source: https://osv.dev/vulnerability/CVE-2022-41958
Type: osv

## Details
super-xray is a web vulnerability scanning tool. Versions prior to 0.7 assumed trusted input for the program config which is stored in a yaml file. An attacker with local access to the file could exploit this and compromise the program. This issue has been addressed in commit `4d0d5966` and will be included in future releases. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/4ra1n/super-xray/security/advisories/GHSA-39pv-4vmj-c4fr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41958.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41958
- https://github.com/4ra1n/super-xray/commit/4d0d59663596db03f39d7edd2be251d48b52dcfc
