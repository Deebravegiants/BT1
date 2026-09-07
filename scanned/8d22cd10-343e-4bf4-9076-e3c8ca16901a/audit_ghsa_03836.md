# [M] Haml vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-r53w-g4xm-3gc6
CVE: CVE-2017-1002201
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-10-21
Source: https://github.com/advisories/GHSA-r53w-g4xm-3gc6
Type: github-advisory

## Affected
- RubyGems: `haml` — affected >=0 <5.0.0

## Details
In haml versions prior to version 5.0.0.beta.2, when using user input to perform tasks on the server, characters like `< > " '` must be escaped properly. In this case, the `'` character was missed. An attacker can manipulate the input to introduce additional attributes, potentially executing code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1002201
- https://github.com/haml/haml/commit/18576ae6e9bdcb4303fdbe6b3199869d289d67c2
- https://github.com/haml/haml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/haml/CVE-2017-1002201.yml
- https://lists.debian.org/debian-lts-announce/2019/11/msg00007.html
- https://lists.debian.org/debian-lts-announce/2021/12/msg00028.html
- https://security.gentoo.org/glsa/202007-27
- https://snyk.io/vuln/SNYK-RUBY-HAML-20362
