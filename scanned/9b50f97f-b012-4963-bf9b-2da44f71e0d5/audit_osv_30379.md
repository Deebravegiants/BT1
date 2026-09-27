# [M] Arbitrary File Write leading up to remote code execution (instructor accounts)

## Summary
Severity: Medium
Advisory: CVE-2024-51743
Aliases: GHSA-hwgg-qvjx-572x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2024-11-18
Source: https://osv.dev/vulnerability/CVE-2024-51743
Type: osv

## Details
MarkUs is a web application for the submission and grading of student assignments. In versions prior to 2.4.8, an arbitrary file write vulnerability in the update/upload/create file methods in Controllers allows authenticated instructors to write arbitrary files to any location on the web server MarkUs is running on (depending on the permissions of the underlying filesystem). e.g. This can lead to a delayed remote code execution in case an attacker is able to write a Ruby file into the config/initializers/ subfolder of the Ruby on Rails application. MarkUs v2.4.8 has addressed this issue. No known workarounds are available at the application level aside from upgrading.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51743.json
- https://github.com/MarkUsProject/Markus/security/advisories/GHSA-hwgg-qvjx-572x
- https://nvd.nist.gov/vuln/detail/CVE-2024-51743
- https://github.com/MarkUsProject/Markus/pull/7026
