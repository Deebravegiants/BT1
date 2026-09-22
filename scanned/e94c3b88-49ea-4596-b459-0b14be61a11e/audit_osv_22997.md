# [H] Autolab is vulnerable to remote code execution (RCE) via MOSS functionality

## Summary
Severity: High
Advisory: CVE-2022-41955
Aliases: GHSA-x5r3-vf3p-3269
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-14
Source: https://osv.dev/vulnerability/CVE-2022-41955
Type: osv

## Details
Autolab is a course management service, initially developed by a team of students at Carnegie Mellon University, that enables instructors to offer autograded programming assignments to their students over the Web. A remote code execution vulnerability was discovered in Autolab's MOSS functionality, whereby an instructor with access to the feature might be able to execute code on the server hosting Autolab. This vulnerability has been patched in version 2.10.0. As a workaround, disable the MOSS feature if it is unneeded by replacing the body of `run_moss` in `app/controllers/courses_controller.rb` with `render(plain: "Feature disabled", status: :bad_request) && return`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41955.json
- https://github.com/autolab/Autolab/security/advisories/GHSA-x5r3-vf3p-3269
- https://nvd.nist.gov/vuln/detail/CVE-2022-41955
- https://securitylab.github.com/advisories/GHSL-2022-100_Autolab/
