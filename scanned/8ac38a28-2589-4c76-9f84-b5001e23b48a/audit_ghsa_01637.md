# [M] OS Command Injection in Rake

## Summary
Severity: Medium
Advisory: GHSA-jppv-gw3r-w3q8
CVE: CVE-2020-8130
CWE: CWE-78
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-02-28
Source: https://github.com/advisories/GHSA-jppv-gw3r-w3q8
Type: github-advisory

## Affected
- RubyGems: `rake` — affected >=0 <12.3.3

## Details
There is an OS command injection vulnerability in Ruby Rake before 12.3.3 in `Rake::FileList` when supplying a filename that begins with the pipe character `|`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8130
- https://github.com/ruby/rake/commit/5b8f8fc41a5d7d7d6a5d767e48464c60884d3aee
- https://hackerone.com/reports/651518
- https://github.com/advisories/GHSA-jppv-gw3r-w3q8
- https://github.com/ruby/rake
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rake/CVE-2020-8130.yml
- https://lists.debian.org/debian-lts-announce/2020/02/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/523CLQ62VRN3VVC52KMPTROCCKY4Z36B
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VXMX4ARNX2JLRJMSH4N3J3UBMUT5CI44
- https://usn.ubuntu.com/4295-1
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00041.html
