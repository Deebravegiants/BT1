# [C] Prototype Pollution in handlebars

## Summary
Severity: Critical
Advisory: GHSA-w457-6q6x-cgp9
CVE: CVE-2019-19919
CWE: CWE-1321, CWE-74
Ecosystem: RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-12-26
Source: https://github.com/advisories/GHSA-w457-6q6x-cgp9
Type: github-advisory

## Affected
- npm: `handlebars` — affected >=4.0.0 <4.3.0
- RubyGems: `bootstrap-wysihtml5-rails` — affected >=0.3.3.5
- npm: `handlebars` — affected >=0 <3.0.8

## Details
Versions of `handlebars` prior to 3.0.8 or 4.3.0 are vulnerable to Prototype Pollution leading to Remote Code Execution. Templates may alter an Objects' `__proto__` and `__defineGetter__` properties, which may allow an attacker to execute arbitrary code through crafted payloads.


## Recommendation

Upgrade to version 3.0.8, 4.3.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-19919
- https://github.com/wycats/handlebars.js/issues/1558
- https://github.com/handlebars-lang/handlebars.js/commit/156061eb7707575293613d7fdf90e2bdaac029ee
- https://github.com/handlebars-lang/handlebars.js/commit/90ad8d97ad2933852fb83fcc054699dc99e094db
- https://github.com/wycats/handlebars.js/commit/2078c727c627f25d4a149962f05c1e069beb18bc
- https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2019-19919
- https://github.com/Nerian/bootstrap-wysihtml5-rails/blob/master/vendor/assets/javascripts/bootstrap-wysihtml5/handlebars.runtime.min.js
- https://github.com/Nerian/bootstrap-wysihtml5-rails/tree/master/vendor/assets/javascripts/bootstrap-wysihtml5
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/bootstrap-wysihtml5-rails/CVE-2019-19919.yml
- https://github.com/wycats/handlebars.js
- https://www.tenable.com/security/tns-2021-14
