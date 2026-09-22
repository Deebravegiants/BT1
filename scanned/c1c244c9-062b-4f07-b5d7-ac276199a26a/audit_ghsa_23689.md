# [M] Puppet uses predictable filenames, allowing arbitrary file overwrite

## Summary
Severity: Medium
Advisory: GHSA-mpmx-gm5v-q789
CVE: CVE-2011-3871
CWE: CWE-340
Ecosystem: RubyGems
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-mpmx-gm5v-q789
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=2.7.0 <2.7.5
- RubyGems: `puppet` — affected >=0 <2.6.11

## Details
Puppet 2.7.x before 2.7.5, 2.6.x before 2.6.11, and 0.25.x, when running in `--edit` mode, uses a predictable file name, which allows local users to run arbitrary Puppet code or trick a user into editing arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3871
- https://github.com/puppetlabs/puppet/commit/343c7bd381b63e042d437111718918f951d9b30d
- https://github.com/puppetlabs/puppet/commit/d76c30935460ded953792dfe49f72b8c5158e899
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2011-3871.yml
- https://puppet.com/security/cve/cve-2011-3871
- http://groups.google.com/group/puppet-announce/browse_thread/thread/91e3b46d2328a1cb
- http://lists.fedoraproject.org/pipermail/package-announce/2011-October/068053.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-October/068061.html
- http://lists.fedoraproject.org/pipermail/package-announce/2011-October/068093.html
- http://www.debian.org/security/2011/dsa-2314
- http://www.ubuntu.com/usn/USN-1223-1
- http://www.ubuntu.com/usn/USN-1223-2
