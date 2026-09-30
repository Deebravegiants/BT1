# [M] Phusion Passenger incorrect permission assignment

## Summary
Severity: Medium
Advisory: GHSA-4284-jfhc-f854
CVE: CVE-2018-12615
CWE: CWE-732
Ecosystem: RubyGems
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-4284-jfhc-f854
Type: github-advisory

## Affected
- RubyGems: `passenger` — affected >=0 <5.3.2

## Details
An issue was discovered in switchGroup() in agent/ExecHelper/ExecHelperMain.cpp in Phusion Passenger before 5.3.2. The set of groups (gidset) is not set correctly, leaving it up to randomness (i.e., uninitialized memory) which supplementary groups are actually being set while lowering privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12615
- https://github.com/phusion/passenger/commit/4e97fdb86d0a0141ec9a052c6e691fcd07bb45c8
- https://github.com/phusion/passenger
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/passenger/CVE-2018-12615.yml
