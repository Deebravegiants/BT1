# [M] canto-saas-api: Authenticated API requests can be redirected via unencoded path variables

## Summary
Severity: Medium
Advisory: GHSA-9qfv-wgh2-m6p8
CVE: CVE-2026-55374
CWE: CWE-74, CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-9qfv-wgh2-m6p8
Type: github-advisory

## Affected
- Packagist: `jleehr/canto-saas-api` — affected >=0 <3.0.0

## Details
## Summary

  In affected versions, `Request::buildRequestUrl()` inserts path variables into
  the request URL without URL encoding (`implode('/', $pathVariables)`). All
  request classes implementing `getPathVariables()` are affected, e.g.
  `GetContentDetailsRequest` (`scheme`, `contentId`).

  If a consuming application passes untrusted input (such as an ID taken from
  an HTTP request parameter) as a path variable, characters like `../`, `?` or
  `#` are sent verbatim and can change the path of the resulting API request.

  ## Impact

  An attacker who controls a path variable value can redirect the
  library's authenticated request — the Bearer access token is attached in
  `AbstractEndpoint::sendRequest()` — to a different API endpoint of the same
  Canto instance, causing unintended reads or writes with the privileges of the
  configured app. The impact depends on how the consuming application sources
  path variable values; applications that only pass trusted, validated IDs are
  not exploitable.

  ## Patches

  Fixed in 3.0.0: every path segment is encoded with `rawurlencode()` before
  being inserted into the request URL.

  ## Workarounds

  If you cannot upgrade, validate untrusted values before passing them to
  request classes, e.g. enforce an allowlist pattern such as
  `^[A-Za-z0-9_-]+$` for content IDs and schemes.

## References
- https://github.com/jleehr/canto-saas-api/security/advisories/GHSA-9qfv-wgh2-m6p8
- https://github.com/jleehr/canto-saas-api
