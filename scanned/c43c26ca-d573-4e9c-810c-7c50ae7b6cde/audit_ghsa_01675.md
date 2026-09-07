# [H] Possible Strong Parameters Bypass in ActionPack

## Summary
Severity: High
Advisory: GHSA-8727-m6gj-mc37
CVE: CVE-2020-8164
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2020-05-26
Source: https://github.com/advisories/GHSA-8727-m6gj-mc37
Type: github-advisory

## Affected
- RubyGems: `actionpack` — affected >=5.0.0 <5.2.4.3
- RubyGems: `actionpack` — affected >=6.0.0 <6.0.3.1

## Details
There is a strong parameters bypass vector in ActionPack.

Versions Affected:  rails <= 6.0.3
Not affected:       rails < 5.0.0
Fixed Versions:     rails >= 5.2.4.3, rails >= 6.0.3.1

Impact
------
In some cases user supplied information can be inadvertently leaked from
Strong Parameters.  Specifically the return value of `each`, or `each_value`,
or `each_pair` will return the underlying "untrusted" hash of data that was
read from the parameters.  Applications that use this return value may be
inadvertently use untrusted user input.

Impacted code will look something like this:

```
def update
  # Attacker has included the parameter: `{ is_admin: true }`
  User.update(clean_up_params)
end

def clean_up_params
   params.each { |k, v|  SomeModel.check(v) if k == :name }
end
```

Note the mistaken use of `each` in the `clean_up_params` method in the above
example.

Workarounds
-----------
Do not use the return values of `each`, `each_value`, or `each_pair` in your
application.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-8164
- https://hackerone.com/reports/292797
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionpack/CVE-2020-8164.yml
- https://groups.google.com/forum/#!topic/rubyonrails-security/f6ioe4sdpbY
- https://groups.google.com/g/rubyonrails-security/c/f6ioe4sdpbY
- https://lists.debian.org/debian-lts-announce/2020/06/msg00022.html
- https://lists.debian.org/debian-lts-announce/2020/07/msg00013.html
- https://www.debian.org/security/2020/dsa-4766
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00089.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00093.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00107.html
