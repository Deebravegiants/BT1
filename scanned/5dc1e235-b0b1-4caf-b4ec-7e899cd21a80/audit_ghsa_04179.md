# [M] canto-saas-api: OAuth credentials exposed in URL query string and exception messages

## Summary
Severity: Medium
Advisory: GHSA-37pm-83g7-r22v
CVE: CVE-2026-55375
CWE: CWE-209, CWE-598
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-37pm-83g7-r22v
Type: github-advisory

## Affected
- Packagist: `jleehr/canto-saas-api` — affected >=0 <3.0.0

## Details
## Summary

  In affected versions, the OAuth2 token request sends `app_id`, `app_secret`,
  `refresh_token` and `code` as URL query parameters of the POST request to
  `https://oauth.<domain>/oauth/api/oauth2/token`. Request URLs are commonly
  recorded in access logs, proxy logs and APM traces, so the application secret
  and refresh token can be persisted in plain text outside the application's
  control.

  In addition, when the token request fails, the Guzzle exception message —
  which contains the full request URI including the credentials — was passed
  unmodified into the `AuthorizationFailedException` thrown by
  `OAuth2::obtainAccessToken()`. Applications that log exceptions or forward
  them to error trackers (e.g. Sentry) may therefore have recorded the app
  secret in their logs.

  ## Impact

  An attacker with access to web server logs, proxy logs, APM tracing data or
  application error logs of a consumer of this library can obtain the Canto
  `app_secret`, `refresh_token` or authorization `code` and use them to obtain
  access tokens for the Canto tenant.

  ## Patches

  Fixed in 3.0.0:

  - OAuth credentials are sent in the form-encoded POST body instead of the URL
    query string (RFC 6749 §2.3.1). `OAuth2Request::getQueryParams()` now
    returns `null`; the parameters are available via `getFormParams()`.
  - Exception messages are sanitized before being rethrown: the values of
    `app_secret`, `refresh_token` and `code` are masked (including url-encoded,
    differently cased and JSON-embedded variants).

  ## Workarounds

  If you cannot upgrade:

  - Treat web server, proxy and APM logs of systems performing Canto OAuth
    requests as secret material and restrict access to them.
  - Catch `AuthorizationFailedException` in your application and strip the query
    string from the message before logging or forwarding it.

  If your logs may have been exposed, rotate the affected Canto app secret.

## References
- https://github.com/jleehr/canto-saas-api/security/advisories/GHSA-37pm-83g7-r22v
- https://github.com/jleehr/canto-saas-api
