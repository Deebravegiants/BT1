# [M] Pupper does not properly restrict characters in Common Name field of Certificate Signing Request

## Summary
Severity: Medium
Advisory: GHSA-q44r-f2hm-v76v
CVE: CVE-2012-3867
Ecosystem: RubyGems
Published: 2017-10-24
Source: https://github.com/advisories/GHSA-q44r-f2hm-v76v
Type: github-advisory

## Affected
- RubyGems: `puppet` — affected >=0 <2.6.17
- RubyGems: `puppet` — affected >=2.7.0 <2.7.18

## Details
`lib/puppet/ssl/certificate_authority.rb` in Puppet before 2.6.17 and 2.7.x before 2.7.18, and Puppet Enterprise before 2.5.2, does not properly restrict the characters in the Common Name field of a Certificate Signing Request (CSR), which makes it easier for user-assisted remote attackers to trick administrators into signing a crafted agent certificate via ANSI control sequences.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3867
- https://github.com/puppetlabs/puppet/commit/dfedaa5fa841ccf335245a748b347b7c7c236640
- https://github.com/puppetlabs/puppet/commit/f3419620b42080dad3b0be14470b20a972f13c50
- https://bugzilla.redhat.com/show_bug.cgi?id=839158
- https://github.com/puppetlabs/puppet
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puppet/CVE-2012-3867.yml
- https://www.puppet.com/security/cve/cve-2012-3867-insufficient-input-validation
- http://lists.opensuse.org/opensuse-security-announce/2012-08/msg00006.html
- http://lists.opensuse.org/opensuse-updates/2012-07/msg00036.html
- http://puppetlabs.com/security/cve/cve-2012-3867
- http://www.debian.org/security/2012/dsa-2511
- http://www.ubuntu.com/usn/USN-1506-1
