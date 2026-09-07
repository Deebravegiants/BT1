# [M] Tarball permission preservation in puppet

## Summary
Severity: Medium
Advisory: GHSA-vw22-465p-8j5w
CVE: CVE-2017-10689
CWE: CWE-269
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-vw22-465p-8j5w
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=0 <4.10.10
- RubyGems: `puppet` — affected >=5.0.0 <5.3.4

## Details
When installing a module using the system tar, the PMT will filter filesystem permissions to a sane value. This may just be based on the user's umask.

When using minitar, files are unpacked with whatever permissions are in the tarball. This is potentially unsafe, as tarballs can be easily created with weird permissions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-10689
- https://github.com/puppetlabs/puppet/commit/17d9e02da3882e44c1876e2805cf9708481715ee
- https://github.com/puppetlabs/puppet/commit/2f1047f85e22cde139a421bc25d371f2ffc92cb1
- https://access.redhat.com/errata/RHSA-2018:2927
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2017-10689.yml
- https://puppet.com/security/cve/CVE-2017-10689
- https://tickets.puppetlabs.com/browse/PUP-7866
- https://usn.ubuntu.com/3567-1
