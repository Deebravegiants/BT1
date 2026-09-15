# [M] Rubyzip denial of service 

## Summary
Severity: Medium
Advisory: GHSA-5m2v-hc64-56h6
CVE: CVE-2019-16892
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-09-30
Source: https://github.com/advisories/GHSA-5m2v-hc64-56h6
Type: github-advisory

## Affected
- RubyGems: `rubyzip` — affected >=0 <1.3.0

## Details
In Rubyzip before 1.3.0, a crafted ZIP file can bypass application checks on ZIP entry sizes because data about the uncompressed size can be spoofed. This allows attackers to cause a denial of service (disk consumption).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16892
- https://github.com/rubyzip/rubyzip/pull/403
- https://github.com/rubyzip/rubyzip/commit/d65fe7bd283ec94f9d6dc7605f61a6b0dd00f55e
- https://access.redhat.com/errata/RHBA-2019:4047
- https://access.redhat.com/errata/RHSA-2019:4201
- https://github.com/jdleesmiller/ruby-advisory-db/blob/master/gems/rubyzip/CVE-2019-16892.yml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rubyzip/CVE-2019-16892.yml
- https://github.com/rubyzip/rubyzip
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/J45KSFPP6DFVWLC7Z73L7SX735CKZYO6
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MWWPORMSBHZTMP4PGF4DQD22TTKBQMMC
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/X255K6ZBAQC462PQN2ND5HOTTQEJ2G2X
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J45KSFPP6DFVWLC7Z73L7SX735CKZYO6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MWWPORMSBHZTMP4PGF4DQD22TTKBQMMC
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/X255K6ZBAQC462PQN2ND5HOTTQEJ2G2X
