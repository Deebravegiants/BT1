# [H] Remote code execution in Kramdown

## Summary
Severity: High
Advisory: GHSA-52p9-v744-mwjj
CVE: CVE-2021-28834
CWE: CWE-94
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-29
Source: https://github.com/advisories/GHSA-52p9-v744-mwjj
Type: github-advisory

## Affected
- RubyGems: `kramdown` — affected >=1.16.0 <2.3.1

## Details
Kramdown before 2.3.1 does not restrict Rouge formatters to the Rouge::Formatters namespace, and thus arbitrary classes can be instantiated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-28834
- https://github.com/gettalong/kramdown/pull/708
- https://github.com/stanhu/kramdown/commit/d6a1cbcb2caa2f8a70927f176070d126b2422760
- https://github.com/stanhu/kramdown/commit/ff0218aefcf00cd5a389e17e075d36cd46d011e2
- https://about.gitlab.com/releases/2021/03/17/security-release-gitlab-13-9-4-released/#remote-code-execution-via-unsafe-user-controlled-markdown-rendering-options
- https://github.com/gettalong/kramdown/compare/REL_2_3_0...REL_2_3_1
- https://gitlab.com/gitlab-org/gitlab/-/commit/179329b5c3c118924fb242dc449d06b4ed6ccb66
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NJCJVYHPY6LNUFM6LYZIAUIYOMVT5QGV
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S3BBLUIDCUUR3NEE4NJLOCCAV3ALQ3O6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/SYOLQKFL6IJCQLBXV34Z4TI4O54GESPR
- https://www.debian.org/security/2021/dsa-4890
