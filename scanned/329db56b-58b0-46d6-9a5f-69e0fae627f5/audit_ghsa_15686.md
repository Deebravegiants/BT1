# [M] RailsAdmin Cross-site Scripting vulnerability in the list view

## Summary
Severity: Medium
Advisory: GHSA-8qgm-g2vv-vwvc
CVE: CVE-2024-39308
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-08
Source: https://github.com/advisories/GHSA-8qgm-g2vv-vwvc
Type: github-advisory

## Affected
- RubyGems: `rails_admin` — affected >=3.0.0.beta <3.1.3

## Details
### Impact
RailsAdmin list view has the XSS vulnerability, caused by improperly-escaped HTML title attribute.
The issue was originally reported in https://github.com/railsadminteam/rails_admin/issues/3686.

### Patches
Upgrade to [3.1.4](https://rubygems.org/gems/rails_admin/versions/3.1.4). The vulnerability itself was patched in 3.1.3 but it has a functionality issue.
Initially the vulnerability was thought to exist in versions before 3.0, but it didn't. 2.x users can stay on 2.2.1.

### Workarounds
1. Copy the index view (located under the path `app/views/rails_admin/main/index.html.erb`) from the RailsAdmin version you use, and place it into your application by using the same path.
2. Open the view file by an editor, and change the way to populate the td tag:

```diff
               <% properties.map{ |property| property.bind(:object, object) }.each do |property| %>
                 <% value = property.pretty_value %>
-                <td class="<%= [property.sticky? && 'sticky', property.css_class, property.type_css_class].select(&:present?).join(' ') %>" title="<%= value %>">
+                <%= content_tag(:td, class: [property.sticky? && 'sticky', property.css_class, property.type_css_class].select(&:present?), title: strip_tags(value.to_s)) do %>
                   <%= value %>
-                </td>
+                <% end %>
               <% end %>
```

**Note:** The view file created by this needs to be removed after upgrading RailsAdmin afterwards, unless this old view continue to be used. Only do this if you can't upgrade RailsAdmin now for a reason.

### References
https://owasp.org/www-community/attacks/xss/
https://api.rubyonrails.org/classes/ActionView/Helpers/SanitizeHelper.html#method-i-strip_tags

## References
- https://github.com/railsadminteam/rails_admin/security/advisories/GHSA-8qgm-g2vv-vwvc
- https://nvd.nist.gov/vuln/detail/CVE-2024-39308
- https://github.com/railsadminteam/rails_admin/issues/3686
- https://github.com/railsadminteam/rails_admin/commit/b5a287d82e2cbd1737a1a01e11ede2911cce7fef
- https://github.com/railsadminteam/rails_admin/commit/d84b39884059c4ed50197cec8522cca029a17673
- https://github.com/railsadminteam/rails_admin
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rails_admin/CVE-2024-39308.yml
- https://rubygems.org/gems/rails_admin/versions/2.3.0
- https://rubygems.org/gems/rails_admin/versions/3.1.3
