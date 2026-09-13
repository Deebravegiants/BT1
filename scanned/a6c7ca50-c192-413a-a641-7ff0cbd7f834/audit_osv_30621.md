# [M] download_all_submissions allows student to download another student's submissions in Autolab

## Summary
Severity: Medium
Advisory: CVE-2024-53258
Aliases: GHSA-84qc-7773-2gg3
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-25
Source: https://osv.dev/vulnerability/CVE-2024-53258
Type: osv

## Details
Autolab is a course management service that enables auto-graded programming assignments. From Autolab versions v.3.0.0 onward students can download all assignments from another student, as long as they are logged in, using the download_all_submissions feature. This can allow for leakage of submissions to unauthorized users, such as downloading submissions from other students in the class, or even instructor test submissions, given they know their user IDs. This issue has been patched in commit `1aa4c769` which is not yet in a release version, but is expected to be included in version 3.0.3. Users are advised to either manually patch or to wait for version 3.0.3. As a workaround administrators can disable the feature.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53258.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-84qc-7773-2gg3
- https://nvd.nist.gov/vuln/detail/CVE-2024-53258
- https://github.com/autolab/Autolab/commit/1aa4c7690892fb458d2c61ff86739f368e34769d
