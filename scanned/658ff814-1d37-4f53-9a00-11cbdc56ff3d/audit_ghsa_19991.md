# [H] active_attr Improper Resource Shutdown or Release vulnerability

## Summary
Severity: High
Advisory: GHSA-4whf-rmx5-8frv
CVE: CVE-2021-4250
CWE: CWE-404
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-12-19
Source: https://github.com/advisories/GHSA-4whf-rmx5-8frv
Type: github-advisory

## Affected
- RubyGems: `active_attr` — affected >=0 <0.15.4

## Details
A vulnerability classified as problematic has been found in cgriego active_attr up to 0.15.3. This affects the function call of the file lib/active_attr/typecasting/boolean_typecaster.rb of the component Regex Handler. The manipulation of the argument value leads to denial of service. The exploit has been disclosed to the public and may be used. Upgrading to version 0.15.4 can address this issue. The name of the patch is dab95e5843b01525444b82bd7b336ef1d79377df. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-216207.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4250
- https://github.com/cgriego/active_attr/issues/184
- https://github.com/cgriego/active_attr/pull/185
- https://github.com/cgriego/active_attr/commit/dab95e5843b01525444b82bd7b336ef1d79377df
- https://github.com/cgriego/active_attr
- https://github.com/cgriego/active_attr/releases/tag/v0.15.3
- https://github.com/cgriego/active_attr/releases/tag/v0.15.4
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/active_attr/CVE-2021-4250.yml
- https://vuldb.com/?id.216207
