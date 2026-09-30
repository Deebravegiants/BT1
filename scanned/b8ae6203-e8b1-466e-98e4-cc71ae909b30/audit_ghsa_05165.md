# [H] Symfony: Security Firewall Bypass via failure_forward Subrequest: Unauthenticated Access to access_control-Protected GET Routes

## Summary
Severity: High
Advisory: GHSA-6h46-9jf5-q59x
CVE: CVE-2026-48489
CWE: CWE-863
Ecosystem: Packagist
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-6h46-9jf5-q59x
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=0 <5.4.53
- Packagist: `symfony/symfony` — affected >=0 <5.4.53
- Packagist: `symfony/security-http` — affected >=6.0.0 <6.4.41
- Packagist: `symfony/security-http` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/security-http` — affected >=8.0.0 <8.0.13
- Packagist: `symfony/symfony` — affected >=6.0.0 <6.4.41
- Packagist: `symfony/symfony` — affected >=7.0.0 <7.4.13
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.13

## Details
### Description

When a firewall is configured with `form-login` (or any authenticator using `DefaultAuthenticationFailureHandler`) and the `failure_forward: true` option, the handler reads the `_failure_path` parameter from the failing login request and uses it as the path of an internal subrequest dispatched through `HttpKernelInterface::SUB_REQUEST`.

Symfony's `Firewall::onKernelRequest` listener intentionally skips subrequests under the assumption they are internally generated and trusted, which also means `AccessListener` (the listener that evaluates `access_control`) does not run. Because the attacker controls the target of the subrequest, an unauthenticated POST to the check path with `_failure_path=/admin/whatever` performs a local request forgery that executes the target controller outside the firewall perimeter and returns its response to the caller.

Applications that follow Symfony's recommended best practice of protecting administrative areas with broad `access_control` rules (e.g. `^/admin` requires `ROLE_ADMIN`) and expose read-only GET endpoints under that area (data exports, internal APIs, account views) are fully exposed: any such GET route can be read by an unauthenticated attacker without any developer misconfiguration, debug mode, or state-changing GET handler being required.

### Resolution

`DefaultAuthenticationFailureHandler` no longer honors the request-supplied `_failure_path` parameter when `failure_forward` is enabled. The subrequest is always dispatched to the configured `failure_path` option (defaulting to `login_path`), which is set by the application owner and not by the request. The redirect branch (`failure_forward: false`) is unchanged because redirects re-enter the firewall on the next request and are not subject to this bypass.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/c48a4276309e11aedeeb0ce3a89dfbf0b4fe04ff) for branch 5.4.

### Credits

Symfony would like to thank Nguyen Ngoc Toan Thang (@a-tt-om) and Tran Quoc Tri Trung (@teebow1e) for reporting the issue, and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-6h46-9jf5-q59x
- https://github.com/symfony/symfony/commit/c48a4276309e11aedeeb0ce3a89dfbf0b4fe04ff
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2026-48489.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-48489.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-48489
