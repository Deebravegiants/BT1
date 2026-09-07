# [M] Netflix Security Monkey Open Redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j6jq-3q8p-xgg6
CVE: CVE-2017-7266
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j6jq-3q8p-xgg6
Type: github-advisory

## Affected
- PyPI: `security_monkey` — affected >=0 <0.8.0

## Details
Netflix Security Monkey before 0.8.0 has an Open Redirect. The logout functionality accepted the "next" parameter which then redirects to any domain irrespective of the Host header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7266
- https://github.com/Netflix/security_monkey/pull/482
- https://github.com/Netflix/security_monkey/commit/3b4da13efabb05970c80f464a50d3c1c12262466
- https://github.com/Netflix/security_monkey
- https://github.com/Netflix/security_monkey/releases/tag/v0.8.0
- https://web.archive.org/web/20201220170714/http://www.securityfocus.com/bid/97088
