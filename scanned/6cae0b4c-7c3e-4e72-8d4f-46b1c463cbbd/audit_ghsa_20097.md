# [M] keynote Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-399p-vq28-5hg8
CVE: CVE-2017-20159
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-31
Source: https://github.com/advisories/GHSA-399p-vq28-5hg8
Type: github-advisory

## Affected
- RubyGems: `keynote` — affected >=0 <1.0.0

## Details
A vulnerability was found in rf Keynote up to 0.x. It has been rated as problematic. Affected by this issue is some unknown functionality of the file lib/keynote/rumble.rb. The manipulation of the argument value leads to cross site scripting. The attack may be launched remotely. Upgrading to version 1.0.0 can address this issue. The name of the patch is 05be4356b0a6ca7de48da926a9b997beb5ffeb4a. It is recommended to upgrade the affected component. VDB-217142 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-20159
- https://github.com/rf-/keynote/commit/05be4356b0a6ca7de48da926a9b997beb5ffeb4a
- https://github.com/rf-/keynote
- https://github.com/rf-/keynote/releases/tag/v1.0.0
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/keynote/CVE-2017-20159.yml
- https://vuldb.com/?ctiid.217142
- https://vuldb.com/?id.217142
