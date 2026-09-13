# [M] Autolab tar slip in Install Assessment functionality (`GHSL-2023-081`)

## Summary
Severity: Medium
Advisory: CVE-2023-32676
Aliases: GHSA-x9hj-r9q4-832c
CVSS: 6.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:H/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/CVE-2023-32676
Type: osv

## Details
Autolab is a course management service that enables auto-graded programming assignments. A Tar slip vulnerability was found in the Install assessment functionality of Autolab. To exploit this vulnerability an authenticated attacker with instructor permissions needs to upload a specially crafted Tar file. Using the install assessment functionality an attacker can feed a Tar file that contain files with paths pointing outside of the target directory (e.g.,  `../../../../tmp/tarslipped1.sh`). When the Install assessment form is submitted the files inside of the archives are expanded to the attacker-chosen locations. This issue has been addressed in version 2.11.0. Users are advised to upgrade.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/32xxx/CVE-2023-32676.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-x9hj-r9q4-832c
- https://nvd.nist.gov/vuln/detail/CVE-2023-32676
- https://securitylab.github.com/advisories/GHSL-2023-081_GHSL-2023-082_Autolab/
- https://github.com/autolab/Autolab/commit/14f508484a8323eceb0cf3a128573b43eabbc80d
