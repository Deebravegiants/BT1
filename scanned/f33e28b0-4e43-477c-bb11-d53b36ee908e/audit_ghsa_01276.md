# [M] XSS in Action View

## Summary
Severity: Medium
Advisory: GHSA-cfjv-5498-mph5
CVE: CVE-2020-15169
CWE: CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-09-11
Source: https://github.com/advisories/GHSA-cfjv-5498-mph5
Type: github-advisory

## Affected
- RubyGems: `actionview` — affected >=0 <5.2.4.4
- RubyGems: `actionview` — affected >=6.0.0.0 <6.0.3.3

## Details
There is a potential Cross-Site Scripting (XSS) vulnerability in Action View's translation helpers. Views that allow the user to control the default (not found) value of the `t` and `translate` helpers could be susceptible to XSS attacks.

### Impact

When an HTML-unsafe string is passed as the default for a missing translation key [named `html` or ending in `_html`](https://guides.rubyonrails.org/i18n.html#using-safe-html-translations), the default string is incorrectly marked as HTML-safe and not escaped. Vulnerable code may look like the following examples:

```erb
<%# The welcome_html translation is not defined for the current locale: %>
<%= t("welcome_html", default: untrusted_user_controlled_string) %>

<%# Neither the title.html translation nor the missing.html translation is defined for the current locale: %>
<%= t("title.html", default: [:"missing.html", untrusted_user_controlled_string]) %>
```

### Patches

Patched Rails versions, 6.0.3.3 and 5.2.4.4, are available from the normal locations.

The patches have also been applied to the `master`, `6-0-stable`, and `5-2-stable` branches on GitHub. If you track any of these branches, you should update to the latest.

To aid users who aren’t able to upgrade immediately, we’ve provided patches for the two supported release series. They are in git-am format and consist of a single changeset.

* [5-2-translate-helper-xss.patch](https://gist.github.com/georgeclaghorn/a466e103922ee81f24c32c9034089442#file-5-2-translate-helper-xss-patch) — patch for the 5.2 release series
* [6-0-translate-helper-xss.patch](https://gist.github.com/georgeclaghorn/a466e103922ee81f24c32c9034089442#file-6-0-translate-helper-xss-patch) — patch for the 6.0 release series

Please note that only the 5.2 and 6.0 release series are currently supported. Users of earlier, unsupported releases are advised to update as soon as possible, as we cannot provide security fixes for unsupported releases.

### Workarounds

Impacted users who can’t upgrade to a patched Rails version can avoid this issue by manually escaping default translations with the `html_escape` helper (aliased as `h`):

```erb
<%= t("welcome_html", default: h(untrusted_user_controlled_string)) %>
```

## References
- https://github.com/rails/rails/security/advisories/GHSA-cfjv-5498-mph5
- https://nvd.nist.gov/vuln/detail/CVE-2020-15169
- https://github.com/rails/rails/commit/e663f084460ea56c55c3dc76f78c7caeddeeb02e
- https://github.com/rails/rails
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/actionview/CVE-2020-15169.yml
- https://groups.google.com/g/rubyonrails-security/c/b-C9kSGXYrc
- https://lists.debian.org/debian-lts-announce/2020/10/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XJ7NUWXAEVRQCROIIBV4C6WXO6IR3KSB
- https://www.debian.org/security/2020/dsa-4766
