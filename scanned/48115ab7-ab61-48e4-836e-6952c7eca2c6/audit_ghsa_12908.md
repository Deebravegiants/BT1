# [H] Denial of Service Vulnerability in ActiveRecord's PostgreSQL adapter

## Summary
Severity: High
Advisory: GHSA-579w-22j4-4749
CVE: CVE-2022-44566
CWE: CWE-400
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-18
Source: https://github.com/advisories/GHSA-579w-22j4-4749
Type: github-advisory

## Affected
- RubyGems: `activerecord` — affected >=0 <6.1.7.1
- RubyGems: `activerecord` — affected >=7.0.0 <7.0.4.1

## Details
There is a potential denial of service vulnerability present in ActiveRecord's PostgreSQL adapter.

This has been assigned the CVE identifier CVE-2022-44566.

Versions Affected: All. Not affected: None.

## Fixed Versions

- 2.3.18.47 (Rails LTS, which is a paid service and not part of the rubygem)
- 3.2.22.34 (Rails LTS, which is a paid service and not part of the rubygem)
- 4.2.11.27 (Rails LTS, which is a paid service and not part of the rubygem)
- 5.2.8.15 (Rails LTS, which is a paid service and not part of the rubygem)
- 6.1.7.1
- 7.0.4.1

## Impact

In ActiveRecord < 7.0.4.1 and < 6.1.7.1, when a value outside the range for a 64bit signed integer is provided to the PostgreSQL connection adapter, it will treat the target column type as numeric. Comparing integer values against numeric values can result in a slow sequential scan resulting in potential Denial of Service.

## Releases

The fixed releases are available at the normal locations.

## Workarounds

Ensure that user supplied input which is provided to ActiveRecord clauses do not contain integers wider than a signed 64bit representation or floats. 

## Patches

To aid users who aren't able to upgrade immediately we have provided patches for the supported release series in accordance with our maintenance policy 1 regarding security issues. They are in git-am format and consist of a single changeset.

 6-1-Added-integer-width-check-to-PostgreSQL-Quoting.patch - Patch for 6.1 series
 7-0-Added-integer-width-check-to-PostgreSQL-Quoting.patch - Patch for 7.0 series

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-44566
- https://github.com/rails/rails/commit/4f44aa9d514e701ada92b5cf08beccf566eeaebf
- https://github.com/rails/rails/commit/82bcdc011e2ff674e7dd8fd8cee3a831c908d29b
- https://code.jeremyevans.net/2022-11-01-forcing-sequential-scans-on-postgresql.html
- https://discuss.rubyonrails.org/t/cve-2022-44566-possible-denial-of-service-vulnerability-in-activerecords-postgresql-adapter/82119
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v6.1.7.1
- https://github.com/rails/rails/releases/tag/v7.0.4.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activerecord/CVE-2022-44566.yml
- https://mailchi.mp/railslts/rails-lts-multiple-dos-vulnerabilities-in-rails-rack-and-globalid
- https://makandracards.com/railslts/508019-rails-5-2-lts-changelog#section-jan-20th-2023-rails-version-5-2-8-15
- https://rubyonrails.org/2023/1/17/Rails-Versions-6-0-6-1-6-1-7-1-7-0-4-1-have-been-released
