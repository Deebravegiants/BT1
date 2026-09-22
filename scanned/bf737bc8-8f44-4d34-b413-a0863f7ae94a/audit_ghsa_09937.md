# [C] Rack::Session::Cookie secrets: decrypt failure fallback enables secretless session forgery and Marshal deserialization

## Summary
Severity: Critical
Advisory: GHSA-33qg-7wpp-89cq
CVE: CVE-2026-39324
CWE: CWE-287, CWE-345, CWE-502, CWE-565
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-33qg-7wpp-89cq
Type: github-advisory

## Affected
- RubyGems: `rack-session` — affected >=2.0.0 <2.1.2

## Details
`Rack::Session::Cookie` incorrectly handles decryption failures when configured with `secrets:`. If cookie decryption fails, the implementation falls back to a default decoder instead of rejecting the cookie. This allows an unauthenticated attacker to supply a crafted session cookie that is accepted as valid session data without knowledge of any configured secret.

Because this mechanism is used to load session state, an attacker can manipulate session contents and potentially gain unauthorized access.

## Details

When `secrets:` is configured, `Rack::Session::Cookie` attempts to decrypt incoming session cookies using one of the configured encryptors. If all decrypt attempts fail, the implementation does not reject the cookie. Instead, it falls back to decoding the cookie using a default coder.

This fallback path processes attacker-controlled cookie data as trusted session state. The behavior is implicit and occurs even when encrypted cookies are expected.

The fallback decoder is applied automatically and does not require the application to opt into a non-encrypted session format. As a result, a client can send a specially crafted cookie value that bypasses the intended integrity protections provided by `secrets:`.

This issue affects both default configurations and those using alternative serializers for encrypted payloads.

## Impact

Any Rack application using `Rack::Session::Cookie` with `secrets:` may be affected.

> [!NOTE]
> Rails applications are typically not affected — Rails uses `ActionDispatch::Session::CookieStore`, which is a separate implementation backed by `ActiveSupport::MessageEncryptor` and does not share the vulnerable code path.

An unauthenticated attacker can supply a crafted session cookie that is accepted as valid session data. This can lead to authentication bypass or privilege escalation in applications that rely on session values for identity or authorization decisions.

Depending on application behavior and available runtime components, processing of untrusted session data may also expose additional risks.

## Mitigation

* Update to a patched version of`rack-session` that rejects cookies when decryption fails under the `secrets:` configuration.
  * After updating, rotate session secrets to invalidate existing session cookies, since attacker-supplied session data may have been accepted and re-issued prior to the fix.

## References
- https://github.com/rack/rack-session/security/advisories/GHSA-33qg-7wpp-89cq
- https://nvd.nist.gov/vuln/detail/CVE-2026-39324
- https://github.com/rack/rack-session
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack-session/CVE-2026-39324.yml
