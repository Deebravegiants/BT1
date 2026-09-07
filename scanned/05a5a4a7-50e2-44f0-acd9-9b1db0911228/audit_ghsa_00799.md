# [C] Unintended read access in kramdown gem

## Summary
Severity: Critical
Advisory: GHSA-mqm2-cgpr-p4m6
CVE: CVE-2020-14001
CWE: CWE-862
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-07
Source: https://github.com/advisories/GHSA-mqm2-cgpr-p4m6
Type: github-advisory

## Affected
- RubyGems: `kramdown` — affected >=0 <2.3.0

## Details
The kramdown gem before 2.3.0 for Ruby processes the template option inside Kramdown documents by default, which allows unintended read access (such as template="/etc/passwd") or unintended embedded Ruby code execution (such as a string that begins with template="string://<%= `). NOTE: kramdown is used in Jekyll, GitLab Pages, GitHub Pages, and Thredded Forum.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-14001
- https://github.com/gettalong/kramdown/commit/1b8fd33c3120bfc6e5164b449e2c2fc9c9306fde
- https://github.com/advisories/GHSA-mqm2-cgpr-p4m6
- https://github.com/gettalong/kramdown
- https://github.com/gettalong/kramdown/compare/REL_2_2_1...REL_2_3_0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/kramdown/CVE-2020-14001.yml
- https://kramdown.gettalong.org
- https://kramdown.gettalong.org/news.html
- https://lists.apache.org/thread.html/r96df7899fbb456fe2705882f710a0c8e8614b573fbffd8d12e3f54d2@%3Cnotifications.fluo.apache.org%3E
- https://lists.debian.org/debian-lts-announce/2020/08/msg00014.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ENMMGKHRQIZ3QKGOMBBBGB6B4LB5I7NQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KBLTGBYU7NKOUOHDKVCU4GFZMGA6BP4L
- https://rubygems.org/gems/kramdown
- https://security.netapp.com/advisory/ntap-20200731-0004
- https://usn.ubuntu.com/4562-1
- https://www.debian.org/security/2020/dsa-4743
