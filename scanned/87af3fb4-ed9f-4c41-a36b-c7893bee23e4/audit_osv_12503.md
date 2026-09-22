# [C] CVE-2018-12557

## Summary
Severity: Critical
Advisory: CVE-2018-12557
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-19
Source: https://osv.dev/vulnerability/CVE-2018-12557
Type: osv

## Details
An issue was discovered in Zuul 3.x before 3.1.0. If nodes become offline during the build, the no_log attribute of a task is ignored. If the unreachable error occurred in a task used with a loop variable (e.g., with_items), the contents of the loop items would be printed in the console. This could lead to accidentally leaking credentials or secrets.

## References
- https://storyboard.openstack.org/#%21/story/2002177
- http://lists.zuul-ci.org/pipermail/zuul-announce/2018-June/000015.html
- https://git.zuul-ci.org/cgit/zuul/commit/?id=ffe7278c08e6e36bf8b18f732c764e00ff51551e
