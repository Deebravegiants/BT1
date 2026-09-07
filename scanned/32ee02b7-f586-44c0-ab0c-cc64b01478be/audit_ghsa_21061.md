# [M] jQuery UI vulnerable to XSS when refreshing a checkboxradio with an HTML-like initial text label

## Summary
Severity: Medium
Advisory: GHSA-h6gj-6jjq-h8g9
CVE: CVE-2022-31160
CWE: CWE-79
Ecosystem: Maven, NuGet, RubyGems, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-07-18
Source: https://github.com/advisories/GHSA-h6gj-6jjq-h8g9
Type: github-advisory

## Affected
- npm: `jquery-ui` — affected >=0 <1.13.2
- Maven: `org.webjars.npm:jquery-ui` — affected >=0 <1.13.2
- RubyGems: `jquery-ui-rails` — affected >=0 <8.0.0
- NuGet: `jQuery.UI.Combined` — affected >=0 <1.13.2

## Details
### Impact
Initializing a checkboxradio widget on an input enclosed within a label makes that parent label contents considered as the input label. If you call `.checkboxradio( "refresh" )` on such a widget and the initial HTML contained encoded HTML entities, they will erroneously get decoded. This can lead to potentially executing JavaScript code.

For example, starting with the following initial secure HTML:
```html
<label>
	<input id="test-input">
	&lt;img src=x onerror="alert(1)"&gt;
</label>
```
and calling:
```js
$( "#test-input" ).checkboxradio();
$( "#test-input" ).checkboxradio( "refresh" );
```
will turn the initial HTML into:
```html
<label>
	<!-- some jQuery UI elements -->
	<input id="test-input">
	<img src=x onerror="alert(1)">
</label>
```
and the alert will get executed.

### Patches
The bug has been patched in jQuery UI 1.13.2.

### Workarounds
To remediate the issue, if you can change the initial HTML, you can wrap all the non-input contents of the `label` in a `span`:
```html
<label>
	<input id="test-input">
	<span>&lt;img src=x onerror="alert(1)"&gt;</span>
</label>
```

### References
https://blog.jqueryui.com/2022/07/jquery-ui-1-13-2-released/

### For more information
If you have any questions or comments about this advisory, search for a relevant issue in [the jQuery UI repo](https://github.com/jquery/jquery-ui/issues?q=is%3Aissue+is%3Aopen+sort%3Aupdated-desc). If you don't find an answer, open a new issue.

## References
- https://github.com/jquery/jquery-ui/security/advisories/GHSA-h6gj-6jjq-h8g9
- https://nvd.nist.gov/vuln/detail/CVE-2022-31160
- https://github.com/jquery/jquery-ui/commit/8cc5bae1caa1fcf96bf5862c5646c787020ba3f9
- https://blog.jqueryui.com/2022/07/jquery-ui-1-13-2-released
- https://github.com/jquery-ui-rails/jquery-ui-rails/blob/master/VERSIONS.md
- https://github.com/jquery-ui-rails/jquery-ui-rails/releases/tag/v8.0.0-release
- https://github.com/jquery/jquery-ui
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/jquery-ui-rails/CVE-2022-31160.yml
- https://lists.debian.org/debian-lts-announce/2022/12/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6XBR3G3JR5ZIOJDO4224M3INXDS2VFDD
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/J5LGNTICB5BRFAG3DHVVELS6H3CZSQMO
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QB2FJQXCNHO32VGVOC6DY6IPGVE4VDU6
- https://security.netapp.com/advisory/ntap-20220909-0007
- https://www.drupal.org/sa-contrib-2022-052
