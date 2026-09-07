# [M] view_component Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-wf2x-8w6j-qw37
CVE: CVE-2024-21636
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-01-04
Source: https://github.com/advisories/GHSA-wf2x-8w6j-qw37
Type: github-advisory

## Affected
- RubyGems: `view_component` — affected >=3.0.0 <3.9.0
- RubyGems: `view_component` — affected >=0 <2.83.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

This is an XSS vulnerability that has the potential to impact anyone rendering a component directly from a controller with the view_component gem. Note that only components that define a [`#call` method](https://viewcomponent.org/guide/templates.html#call) (i.e. instead of using a sidecar template) are affected. The return value of the `#call` method is not sanitized and can include user-defined content.

In addition, the return value of the [`#output_postamble` method](https://viewcomponent.org/api.html#output_postamble--string) is not sanitized, which can also lead to XSS issues.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Versions 3.9.0 has been released and fully mitigates both the `#call` and the `#output_postamble` vulnerabilities.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Sanitize the return value of `#call`, eg:

```ruby
class MyComponent < ApplicationComponent
  def call
    html_escape("<div>#{user_input}</div>")
  end
end
```

### References
_Are there any links users can visit to find out more?_

https://github.com/ViewComponent/view_component/pull/1950

### For more information

If you have any questions or comments about this advisory:

Open an issue in the [github/view_component](https://github.com/github/view_component) project.

## References
- https://github.com/ViewComponent/view_component/security/advisories/GHSA-wf2x-8w6j-qw37
- https://nvd.nist.gov/vuln/detail/CVE-2024-21636
- https://github.com/ViewComponent/view_component/pull/1950
- https://github.com/ViewComponent/view_component/pull/1962
- https://github.com/ViewComponent/view_component/commit/0d26944a8d2730ea40e60eae23d70684483e5017
- https://github.com/ViewComponent/view_component/commit/c43d8bafa7117cbce479669a423ab266de150697
- https://github.com/ViewComponent/view_component
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/view_component/CVE-2024-21636.yml
