# [M] In RubyGem excon, interrupted Persistent Connections May Leak Response Data

## Summary
Severity: Medium
Advisory: GHSA-q58g-455p-8vw9
CVE: CVE-2019-16779
CWE: CWE-362, CWE-664
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2019-12-16
Source: https://github.com/advisories/GHSA-q58g-455p-8vw9
Type: github-advisory

## Affected
- RubyGems: `excon` — affected >=0 <0.71.0

## Details
### Impact
There was a race condition around persistent connections, where a connection which is interrupted (such as by a timeout) would leave data on the socket. Subsequent requests would then read this data, returning content from the previous response. The race condition window appears to be short, and it would be difficult to purposefully exploit this.

### Patches
The problem has been patched in 0.71.0, users should upgrade to this or a newer version (if one exists).

### Workarounds
Users can workaround the problem by disabling persistent connections, though this may cause performance implications.

### References
See the [patch](https://github.com/excon/excon/commit/ccb57d7a422f020dc74f1de4e8fb505ab46d8a29) for further details.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [excon/issues](https://github.com/excon/excon/issues)
* Email us at [geemus+github@gmail.com](mailto:geemus+github@gmail.com)

## References
- https://github.com/excon/excon/security/advisories/GHSA-q58g-455p-8vw9
- https://nvd.nist.gov/vuln/detail/CVE-2019-16779
- https://github.com/excon/excon/commit/ccb57d7a422f020dc74f1de4e8fb505ab46d8a29
- https://github.com/excon/excon
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/excon/CVE-2019-16779.yml
- https://lists.debian.org/debian-lts-announce/2020/01/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2020-01/msg00062.html
