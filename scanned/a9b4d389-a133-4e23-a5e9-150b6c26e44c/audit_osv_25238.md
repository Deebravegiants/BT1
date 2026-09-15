# [M] Autolab tar slip in cheat checker functionality (`GHSL-2023-082`)

## Summary
Severity: Medium
Advisory: CVE-2023-32317
Aliases: GHSA-h8g5-vhm4-wx6g
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-32317
Type: osv

## Details
Autolab is a course management service that enables auto-graded programming assignments. A Tar slip vulnerability was found in the MOSS cheat checker functionality of Autolab. To exploit this vulnerability an authenticated attacker with instructor permissions needs to upload a specially crafted Tar file. Both "Base File Tar" and "Additional file archive" can be fed with Tar files that contain paths outside their target directories (e.g.,  `../../../../tmp/tarslipped2.sh`). When the MOSS cheat checker is started the files inside of the archives are expanded to the attacker-chosen locations. This issue may lead to arbitrary file write within the scope of the running process.  This issue has been addressed in version 2.11.0. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32317.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-h8g5-vhm4-wx6g
- https://nvd.nist.gov/vuln/detail/CVE-2023-32317
- https://securitylab.github.com/advisories/GHSL-2023-081_GHSL-2023-082_Autolab/
- https://github.com/autolab/Autolab/commit/410a9228ee265f80692334d75eb2c3b4dac6f9e5
