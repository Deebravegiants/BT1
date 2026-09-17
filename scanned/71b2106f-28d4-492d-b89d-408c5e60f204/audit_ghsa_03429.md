# [H] Pgsync Contains Cleartext Transmission of Sensitive Information

## Summary
Severity: High
Advisory: GHSA-72rj-36qc-47g7
CVE: CVE-2021-31671
CWE: CWE-319
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-04-27
Source: https://github.com/advisories/GHSA-72rj-36qc-47g7
Type: github-advisory

## Affected
- RubyGems: `pgsync` — affected >=0 <0.6.7

## Details
pgsync before 0.6.7 is affected by Information Disclosure of sensitive information. Syncing the schema with the `--schema-first` and `--schema-only` options is mishandled. For example, the sslmode connection parameter may be lost, which means that SSL would not be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31671
- https://github.com/ankane/pgsync/issues/121
- https://github.com/ankane/pgsync/commit/05cd18f5fc09407e4b544f2c12f819cabc50c40e
- https://github.com/ankane/pgsync/blob/master/CHANGELOG.md#067-2021-04-26
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/pgsync/CVE-2021-31671.yml
