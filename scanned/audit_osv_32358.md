# [M] CVE-2025-28101

## Summary
Severity: Medium
Advisory: CVE-2025-28101
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-04-17
Source: https://osv.dev/vulnerability/CVE-2025-28101
Type: osv

## Details
An arbitrary file deletion vulnerability in the /post/{postTitle} component of flaskBlog v2.6.1 allows attackers to delete article titles created by other users via supplying a crafted POST request.

## References
- https://gist.github.com/coleak2021/cecfc757bc77038717c3e7b40e2d66ce
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/28xxx/CVE-2025-28101.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-28101
- https://github.com/DogukanUrker/flaskBlog/issues/130
