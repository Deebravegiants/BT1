# [C] curupira is vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-85gf-wr67-f83w
CVE: CVE-2015-10053
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-16
Source: https://github.com/advisories/GHSA-85gf-wr67-f83w
Type: github-advisory

## Affected
- RubyGems: `curupira` — affected >=0 <0.1.4

## Details
A vulnerability classified as critical has been found in prodigasistemas curupira up to 0.1.3. Affected is an unknown function of the file app/controllers/curupira/passwords_controller.rb. The manipulation leads to sql injection. Upgrading to version 0.1.4 is able to address this issue. The name of the patch is 93a9a77896bb66c949acb8e64bceafc74bc8c271. It is recommended to upgrade the affected component. VDB-218394 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10053
- https://github.com/prodigasistemas/curupira/commit/93a9a77896bb66c949acb8e64bceafc74bc8c271
- https://github.com/prodigasistemas/curupira
- https://github.com/prodigasistemas/curupira/releases/tag/v0.1.4
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/curupira/CVE-2015-10053.yml
- https://vuldb.com/?ctiid.218394
- https://vuldb.com/?id.218394
