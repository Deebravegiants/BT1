# [M] Puppet allows local users to modify the permissions of arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-qh3g-27jf-3j54
CVE: CVE-2011-3870
CWE: CWE-59
Ecosystem: RubyGems
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qh3g-27jf-3j54
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=2.7.0 <2.7.5
- RubyGems: `puppet` — affected >=0 <2.6.11

## Details
Puppet 2.7.x before 2.7.5, 2.6.x before 2.6.11, and 0.25.x allows local users to modify the permissions of arbitrary files via a symlink attack on the SSH authorized_keys file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3870
- https://github.com/puppetlabs/puppet/commit/88512e880bd2a03694b5fef42540dc7b3da05d30
- https://github.com/puppetlabs/puppet/commit/b29b1785d543a3cea961fffa9b3c15f14ab7cce0
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2011-3870.yml
- https://puppet.com/security/cve/cve-2011-3870
- http://groups.google.com/group/puppet-announce/browse_thread/thread/91e3b46d2328a1cb
- http://lists.fedoraproject.org/pipermail/package-announce/2011-October/068053.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-October/068061.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-October/068093.html
- http://www.debian.org/security/2011/dsa-2314
- http://www.ubuntu.com/usn/USN-1223-1
- http://www.ubuntu.com/usn/USN-1223-2
