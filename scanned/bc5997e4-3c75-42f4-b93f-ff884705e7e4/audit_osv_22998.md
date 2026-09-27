# [M] Autolab is vulnerable to file disclosure via remote handin feature

## Summary
Severity: Medium
Advisory: CVE-2022-41956
Aliases: GHSA-g7x7-mgrv-f24x
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-01-14
Source: https://osv.dev/vulnerability/CVE-2022-41956
Type: osv

## Details
Autolab is a course management service, initially developed by a team of students at Carnegie Mellon University, that enables instructors to offer autograded programming assignments to their students over the Web. A file disclosure vulnerability was discovered in Autolab's remote handin feature, whereby users are able to hand-in assignments using paths outside their submission directory. Users can then view the submission to view the file's contents. The vulnerability has been patched in version 2.10.0. As a workaround, ensure that the field for the remote handin feature is empty (Edit Assessment > Advanced > Remote handin path), and that you are not running Autolab as `root` (or any user that has write access to `/`). Alternatively, disable the remote handin feature if it is unneeded by replacing the body of `local_submit` in `app/controllers/assessment/handin.rb` with `render(plain: "Feature disabled", status: :bad_request) && return`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41956.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-g7x7-mgrv-f24x
- https://nvd.nist.gov/vuln/detail/CVE-2022-41956
- https://securitylab.github.com/advisories/GHSL-2022-100_Autolab/
- https://www.stackhawk.com/blog/rails-path-traversal-guide-examples-and-prevention/
