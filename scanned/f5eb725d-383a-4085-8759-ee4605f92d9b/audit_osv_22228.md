# [H] Insufficient file checks in m1k1o/blog

## Summary
Severity: High
Advisory: CVE-2022-23626
Aliases: GHSA-wmqj-5v54-24x4
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-08
Source: https://osv.dev/vulnerability/CVE-2022-23626
Type: osv

## Details
m1k1o/blog is a lightweight self-hosted facebook-styled PHP blog. Errors from functions `imagecreatefrom*` and `image*` have not been checked properly. Although PHP issued warnings and the upload function returned `false`, the original file (that could contain a malicious payload) was kept on the disk. Users are advised to upgrade as soon as possible. There are no known workarounds for this issue.

## References
- http://packetstormsecurity.com/files/167235/m1k1os-Blog-1.3-Remote-Code-Execution.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23626.json
- https://github.com/m1k1o/blog/security/advisories/GHSA-wmqj-5v54-24x4
- https://nvd.nist.gov/vuln/detail/CVE-2022-23626
- https://github.com/m1k1o/blog/commit/6f5e59f1401c4a3cf2e518aa85b231ea14e8a2ef
