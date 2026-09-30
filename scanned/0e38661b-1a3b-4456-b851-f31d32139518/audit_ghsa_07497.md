# [M] Pagy I18n locale option is not validated before being used in a file path

## Summary
Severity: Medium
Advisory: GHSA-2xmw-f8j8-wfxc
CVE: CVE-2026-54659
CWE: CWE-200, CWE-22
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-2xmw-f8j8-wfxc
Type: github-advisory

## Affected
- RubyGems: `pagy` — affected >=43.0.0 <43.5.6

## Details
### Summary

`Pagy::I18n.locale=` did not validate its argument before using it as a
path component to load the matching dictionary file (`<locale>.yml`). An
application that assigns untrusted input to the locale — e.g. the common
pattern `Pagy::I18n.locale = params[:locale]` — let that input influence
which file Pagy attempted to load.

### Details

The setter stored the value as-is, and the loader joined it into a path
and read it:

```ruby
# gem/lib/pagy/modules/i18n/i18n.rb
def locale=(value)
  Thread.current[:pagy_locale] = value.to_s
end

# ...later, when translating:
path = pathnames.reverse.map { |p| p.join("#{locale}.yml") }.find(&:exist?)
dictionary = YAML.load_file(path)[locale]
```

Because the locale was used verbatim, a value such as an absolute path or
a `../`-style string redirected the lookup outside the locales directory.
Pagy's subsequent structural check (`dictionary['pagy']['p11n']`)
prevents the file's contents from being returned, so this is **not** a
direct file read.

Fixed in 43.5.6 by constraining the locale to a BCP 47 shape before use:

```ruby
LOCALE_PATTERN = /\A[a-zA-Z]{2,8}(-[a-zA-Z0-9]{1,8})*\z/

def locale=(value)
  Thread.current[:pagy_locale] = value.to_s[LOCALE_PATTERN]
end
```

Any non-matching value (including `nil`) resolves to the default locale
and never reaches the file lookup.

### PoC

In an application that sets `Pagy::I18n.locale = params[:locale]`, the
loader appends `.yml` and reads `<locale>.yml`, so the request param
controls the target path. For example, pointing it at the app's
`config/database.yml`:

1. Send a request with `?locale=../../../config/database` (adjust the
   number of `../` to reach the app root from the gem's `locales/`
   directory).
2. Pagy calls `YAML.load_file` on the resulting `…/config/database.yml`.
3. The outcome differs by whether that `.yml` exists, is readable, parses
   as YAML, and has Pagy's expected structure — an existing, readable
   `config/database.yml` raises a different error than a non-existent
   path (which silently falls back to the default locale). This yields a
   file-existence / readability oracle for `.yml` paths, and the targeted
   file is read into the process during the attempt.

### Impact

Information disclosure (CWE-22 / CWE-200): a file-existence / readability
oracle for `.yml` paths on the host, plus a server-side read of
attacker-chosen files into the process. The file contents are not
returned in the response.

Only applications that pass **unsanitized end-user input** into
`Pagy::I18n.locale=` are affected. Applications that set the locale from
trusted values are not affected.

**Patched:** pagy 43.5.6.
**Workaround (if you cannot upgrade):** validate the locale before
assigning it, e.g.
`Pagy::I18n.locale = params[:locale].to_s[/\A[a-zA-Z]{2,8}(-[a-zA-Z0-9]{1,8})*\z/]`,
or restrict it to your known set of locales.

## References
- https://github.com/ddnexus/pagy/security/advisories/GHSA-2xmw-f8j8-wfxc
- https://github.com/ddnexus/pagy/pull/908
- https://github.com/ddnexus/pagy/commit/efcf09690e9fa7d7abdfb987b785a55f87e287df
- https://github.com/ddnexus/pagy
- https://github.com/ddnexus/pagy/releases/tag/43.5.6
