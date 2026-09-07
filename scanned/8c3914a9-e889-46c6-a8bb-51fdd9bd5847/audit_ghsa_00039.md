# [H] Sprockets path traversal leads to information leak

## Summary
Severity: High
Advisory: GHSA-pr3h-jjhj-573x
CVE: CVE-2018-3760
CWE: CWE-200, CWE-22
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-06-20
Source: https://github.com/advisories/GHSA-pr3h-jjhj-573x
Type: github-advisory

## Affected
- RubyGems: `sprockets` — affected >=3.0.0 <3.7.2
- RubyGems: `sprockets` — affected >=4.0.0.beta1 <4.0.0.beta8
- RubyGems: `sprockets` — affected >=0 <2.12.5

## Details
Specially crafted requests can be used to access files that exist on the filesystem that is outside an application's root directory, when the Sprockets server is used in production.
  
All users running an affected release should either upgrade or use one of the work arounds immediately.
  
### Workaround:
  
In Rails applications, work around this issue, set `config.assets.compile = false` and `config.public_file_server.enabled = true` in an initializer and precompile the assets.

This work around will not be possible in all hosting environments and upgrading is advised.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3760
- https://github.com/rails/sprockets/commit/18b8a7f07a50c245e9aee7854ecdbe606bbd8bb5
- https://github.com/rails/sprockets/commit/9c34fa05900b968d74f08ccf40917848a7be9441
- https://github.com/rails/sprockets/commit/c09131cf5b2c479263939c8582e22b98ed616c5f
- https://access.redhat.com/errata/RHSA-2018:2244
- https://access.redhat.com/errata/RHSA-2018:2245
- https://access.redhat.com/errata/RHSA-2018:2561
- https://access.redhat.com/errata/RHSA-2018:2745
- https://github.com/rails/sprockets
- https://groups.google.com/d/msg/rubyonrails-security/ft_J--l55fM/7roDfQ50BwAJ
- https://www.debian.org/security/2018/dsa-4242
