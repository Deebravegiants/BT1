# [H] activeadmin vulnerable to stored persistent cross-site scripting (XSS) in dynamic form legends

## Summary
Severity: High
Advisory: GHSA-9mg6-x45v-hcfm
CVE: CVE-2024-37031
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-02
Source: https://github.com/advisories/GHSA-9mg6-x45v-hcfm
Type: github-advisory

## Affected
- RubyGems: `activeadmin` — affected >=0 <3.2.2
- RubyGems: `activeadmin` — affected >=4.0.0.beta1 <4.0.0.beta7

## Details
### Impact

Users settings their active admin form legends dynamically may be vulnerable to stored XSS, as long as its value can be injected directly by a malicious user.

For example:

* A public web application allows users to create entities with arbitrary names.
* Active Admin is used to administrate these entities through a private backend.
* The form to edit these entities in the private backend has the following shape (note the dynamic `name` value dependent on an attribute of the `resource`):

```ruby
  form do |f|
    f.inputs name: resource.name do
      f.input :name
      f.input :description
    end

    f.actions
  end
```

Then a malicious user could create an entity with a payload that would get executed in the active admin administrator's browser.

Both `form` blocks with an implicit or explicit name (i.e., both `form resource.name` or `form name: resource.name` would suffer from the problem), where the value of the name can be arbitrarily set by non admin users.

### Patches

The problem has been fixed in ActiveAdmin 3.2.2 and ActiveAdmin 4.0.0.beta7.

### Workarounds

Users can workaround this problem without upgrading by explicitly escaping the form name using an HTML escaping utility. For example:

```ruby
  form do |f|
    f.inputs name: ERB::Util.html_escape(resource.name) do
      f.input :name
      f.input :description
    end

    f.actions
  end
```
Upgrading is of course recommended though.

### References
https://owasp.org/www-community/attacks/xss/#stored-xss-attacks

## References
- https://github.com/activeadmin/activeadmin/security/advisories/GHSA-9mg6-x45v-hcfm
- https://nvd.nist.gov/vuln/detail/CVE-2024-37031
- https://github.com/activeadmin/activeadmin/pull/8349
- https://github.com/activeadmin/activeadmin
- https://github.com/activeadmin/activeadmin/releases/tag/v3.2.2
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activeadmin/CVE-2024-37031.yml
- https://rubygems.org/gems/activeadmin/versions/3.2.2
