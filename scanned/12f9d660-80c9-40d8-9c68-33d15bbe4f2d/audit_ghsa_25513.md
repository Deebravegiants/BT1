# [H] SQL injection in blazer

## Summary
Severity: High
Advisory: GHSA-qf9q-q4hh-qph3
CVE: CVE-2022-29498
CWE: CWE-89
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-qf9q-q4hh-qph3
Type: github-advisory

## Affected
- RubyGems: `blazer` — affected >=0 <2.6.0

## Details
Blazer before 2.6.0 allows SQL Injection. In certain circumstances, an attacker could get a user to run a query they would not have normally run.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29498
- https://github.com/ankane/blazer/issues/391
- https://github.com/ankane/blazer/issues/392
- https://github.com/ankane/blazer/commit/f49fbfed7b9e406a69eb78c463c3aa5d35006d8d"
- https://github.com/ankane/blazer
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/blazer/CVE-2022-29498.yml
