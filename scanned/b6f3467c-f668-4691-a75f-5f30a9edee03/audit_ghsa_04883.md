# [M] WebauthnAuthenticator leaks sensitive HTTP headers through INFO-level logs

## Summary
Severity: Medium
Advisory: GHSA-q683-8468-r6h6
CWE: CWE-200, CWE-532
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-q683-8468-r6h6
Type: github-advisory

## Affected
- Packagist: `web-auth/webauthn-symfony-bundle` — affected >=0 <5.3.4

## Details
## Impact

`Webauthn\Bundle\Security\Http\Authenticator\WebauthnAuthenticator` logs the full `Symfony\Component\HttpFoundation\Request` object inside the log context of both `onAuthenticationSuccess()` and `onAuthenticationFailure()` at INFO level:

```php
$this->logger->info('User has been authenticated successfully with Webauthn.', [
    'request' => $request,
    'firewallName' => $firewallName,
    'identifier' => $token->getUserIdentifier(),
]);

$this->logger->info('Webauthn authentication request failed.', [
    'request' => $request,
    'exception' => $exception,
]);
```

`Request::__toString()` returns the raw HTTP message, including every request header. As soon as the configured logger normalises or stringifies the context (default behaviour for `LineFormatter`, `JsonFormatter` via `NormalizerFormatter`, etc.), sensitive headers such as `Cookie` (session identifier), `Authorization` and any custom auth header are written to the log stream in clear text.

Applications that forward logs to centralised platforms (ELK, Splunk, Datadog and similar) are particularly exposed: log access is typically broader than application access, which can allow log readers to hijack authenticated sessions.

## Affected versions

Every release prior to 5.3.4 is affected.

## Patches

The fix removes the full `Request` object from the log context and keeps only non-sensitive fields (request path, method, firewall name, user identifier). It is shipped in 5.3.4. Older branches will not receive a backport; users on those branches should upgrade to 5.3.4+ or apply one of the workarounds below.

## Workarounds

Until the upgrade is applied, projects can:

1. Raise the minimum log level for the WebAuthn authenticator above INFO so these two log records are not emitted in production.
2. Configure their Monolog processor/formatter to strip the `request` key from the context of these records before they are written.

## Credit

Reported by Kay Joosten (Dawn Technology), maintainer of [Stepup-Webauthn](https://github.com/OpenConext/Stepup-Webauthn).

## References
- https://github.com/web-auth/webauthn-framework/security/advisories/GHSA-q683-8468-r6h6
- https://github.com/web-auth/webauthn-framework
