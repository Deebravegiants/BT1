# [C] RubyGems vulnerable to Deserialization of Untrusted Data

## Summary
Severity: Critical
Advisory: GHSA-mqwr-4qf2-2hcv
CVE: CVE-2017-0903
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mqwr-4qf2-2hcv
Type: github-advisory

## Affected
- RubyGems: `rubygems-update` — affected >=2.0.0 <2.6.14

## Details
RubyGems versions between 2.0.0 and 2.6.13 are vulnerable to a possible remote code execution vulnerability. YAML deserialization of gem specifications can bypass class white lists. Specially crafted serialized objects can possibly be used to escalate to remote code execution. The issue has been patched in 2.6.14.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-0903
- https://github.com/rubygems/rubygems/commit/510b1638ac9bba3ceb7a5d73135dafff9e5bab49
- https://hackerone.com/reports/274990
- https://access.redhat.com/errata/RHSA-2017:3485
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0585
- https://github.com/rubygems/rubygems
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://usn.ubuntu.com/3553-1
- https://usn.ubuntu.com/3685-1
- https://web.archive.org/web/20200227143351/http://www.securityfocus.com/bid/101275
- https://www.debian.org/security/2017/dsa-4031
- http://blog.rubygems.org/2017/10/09/2.6.14-released.html
- http://blog.rubygems.org/2017/10/09/unsafe-object-deserialization-vulnerability.html
