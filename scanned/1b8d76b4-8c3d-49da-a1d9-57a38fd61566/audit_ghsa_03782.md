# [C] Improper Input Validation in simple_form

## Summary
Severity: Critical
Advisory: GHSA-r74q-gxcg-73hx
CVE: CVE-2019-16676
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-30
Source: https://github.com/advisories/GHSA-r74q-gxcg-73hx
Type: github-advisory

## Affected
- RubyGems: `simple_form` — affected >=0 <5.0.0

## Details
## Incorrect Access Control in `file_method?` in `lib/simple_form/form_builder.rb`; a user-supplied string is invoked as a method call

### Impact
For pages that build a form using user input, it is possible for an attacker to manipulate the input and send any method present in the form object. For example:

```erb
<%= simple_form_for @user do |f| %>
  <%= f.label @user_supplied_string %>
  ...
<% end %>
```

The string provided in the variable `@user_supplied_string` would be invoked as a method call inside the `@user` object (unless the string contains any of the following: `password`, `time_zone`, `country`, `email`, `phone` and `url`).

By manipulation that input, an attacker could do any of the following:

- Code execution (call actions like `#destroy`)
- Denial of Service (by executing a computation intensive method)
- Information Disclosure (check the presence of methods, leak user information)

### Patches
The problem was fixed in version `5.0`. Although it's a major version, there should be no issues with upgrading for `4.x`. The reason it was released in a major version is that the configuration `SimpleForm.file_methods` was deprecated in order to fix the problem.

### Workarounds
The issue only happens with pages that build forms based on user-provided input. If your application doesn't do that, you're not affected.
A workaround is to explicitly pass which type you want for an input since the issue lies on Simple Form's automatically discovery of input types. This can be done using the `as` option, like the following:
```erb
<%= form.input :avatar, as: :file %>
```

### References
[TDB]

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/plataformatec/simple_form](https://github.com/plataformatec/simple_form)
* Email us at [opensource@plataformatec.com.br](mailto:opensource@plataformatec.com.br)

## References
- https://github.com/plataformatec/simple_form/security/advisories/GHSA-r74q-gxcg-73hx
- https://nvd.nist.gov/vuln/detail/CVE-2019-16676
- https://github.com/heartcombo/simple_form/commit/8c91bd76a5052ddf3e3ab9fd8333f9aa7b2e2dd6
- https://github.com/advisories/GHSA-r74q-gxcg-73hx
- https://github.com/heartcombo/simple_form
- https://github.com/plataformatec/simple_form/commits/master
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/simple_form/CVE-2019-16676.yml
- http://blog.plataformatec.com.br/2019/09/incorrect-access-control-in-simple-form-cve-2019-16676
