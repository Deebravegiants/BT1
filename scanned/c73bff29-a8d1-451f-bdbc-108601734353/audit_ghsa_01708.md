# [H] Exposure of Sensitive Information to an Unauthorized Actor in Doorkeeper

## Summary
Severity: High
Advisory: GHSA-j7vx-8mqj-cqp9
CVE: CVE-2020-10187
CWE: CWE-862
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-05-07
Source: https://github.com/advisories/GHSA-j7vx-8mqj-cqp9
Type: github-advisory

## Affected
- RubyGems: `doorkeeper` — affected >=5.0.0 <5.0.3
- RubyGems: `doorkeeper` — affected >=5.1.0 <5.1.1
- RubyGems: `doorkeeper` — affected >=5.2.0 <5.2.5
- RubyGems: `doorkeeper` — affected >=5.3.0 <5.3.2

## Details
### Impact
Information disclosure vulnerability. Allows an attacker to see all `Doorkeeper::Application` model attribute values (including secrets) using authorized applications controller if it's enabled (GET /oauth/authorized_applications.json).

### Patches

These versions have the fix:

* 5.0.3
* 5.1.1
* 5.2.5
* 5.3.2

### Workarounds
Patch `Doorkeeper::Application` model `#as_json(options = {})` method and define only those attributes you want to expose.

Additional recommended hardening is to enable application secrets hashing ([guide](https://doorkeeper.gitbook.io/guides/security/token-and-application-secrets)), available since Doorkeeper 5.1. This would render the exposed secret useless.

### References

- Commit with fix: https://github.com/doorkeeper-gem/doorkeeper/commit/25d038022c2fcad45af5b73f9d003cf38ff491f6
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-10187

## References
- https://github.com/doorkeeper-gem/doorkeeper/security/advisories/GHSA-j7vx-8mqj-cqp9
- https://nvd.nist.gov/vuln/detail/CVE-2020-10187
- https://github.com/rubysec/ruby-advisory-db/pull/446
- https://github.com/doorkeeper-gem/doorkeeper/commit/25d038022c2fcad45af5b73f9d003cf38ff491f6
- https://github.com/doorkeeper-gem/doorkeeper/releases
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/doorkeeper/CVE-2020-10187.yml
