# [M] Kaminari Insecure File Permissions Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7r3j-qmr4-jfpj
CVE: CVE-2024-32978
CWE: CWE-276
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-28
Source: https://github.com/advisories/GHSA-7r3j-qmr4-jfpj
Type: github-advisory

## Affected
- RubyGems: `kaminari` — affected >=0.15.0 <0.16.2

## Details
A moderate severity security vulnerability has been identified in the Kaminari pagination library for Ruby on Rails, concerning insecure file permissions. This advisory outlines the vulnerability, affected versions, and provides guidance for mitigation.

### Impact

This vulnerability is of moderate severity due to the potential for unauthorized write access to particular Ruby files managed by the library. Such access could lead to the alteration of application behavior or data integrity issues.

### Resolution

Those who use the `gem install` command, such as `gem install kaminari -v 0.16.1`, `gem unpack kaminari -v 0.16.1`, or `bundle install` to download the package would **_not_** be affected and no action is required. 

Those who manually download and decompressing the affected versions are advised to update to 0.16.2 or later version of Kaminari where file permissions have been adjusted to enhance security.

### Workarounds

If upgrading is not feasible immediately, manually adjusting the file permissions on the server to `644` to restrict access is a viable interim measure.

#### All Affected Versions:

```
lib/kaminari/models/page_scope_methods.rb
```

In addition to the previously mentioned files, security tools like AWS Inspector might also identify other files as unsafe. These files, although not loaded or used at runtime, may still be flagged. To avoid any potential confusion in your logs and ensure system integrity, we recommend updating the permissions for these files as well. This proactive measure helps maintain a clean security posture and minimizes unnecessary alerts.

#### Version 0.15.0 and 0.15.1:

```
spec/models/mongo_mapper/mongo_mapper_spec.rb
```

#### Version 0.16.0:

```
spec/models/mongo_mapper/mongo_mapper_spec.rb
spec/models/mongoid/mongoid_spec.rb
```

#### Version 0.16.1:

```
spec/models/active_record/scopes_spec.rb
spec/models/mongo_mapper/mongo_mapper_spec.rb
spec/models/mongoid/mongoid_spec.rb
gemfiles/data_mapper_12.gemfile
gemfiles/active_record_32.gemfile
```

### References

Official Kaminari repository link (this page)

### Acknowledgements

We thank [Gareth Jones](https://github.com/G-Rath) for discovering and reporting this issue. Their diligent work is instrumental in our ongoing efforts to maintain and improve software security.

## References
- https://github.com/kaminari/kaminari/security/advisories/GHSA-7r3j-qmr4-jfpj
- https://nvd.nist.gov/vuln/detail/CVE-2024-32978
- https://github.com/kaminari/kaminari
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/kaminari/CVE-2024-32978.yml
