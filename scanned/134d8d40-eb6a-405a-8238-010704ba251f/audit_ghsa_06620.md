# [C] Poweradmin has Host Header Injection in OIDC redirect_uri, SAML ACS/SLO URL, and Logout Redirect Construction.

## Summary
Severity: Critical
Advisory: GHSA-3735-5339-xfwx
CVE: CVE-2026-54588
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-3735-5339-xfwx
Type: github-advisory

## Affected
- Packagist: `poweradmin/poweradmin` — affected >=0 <4.2.4
- Packagist: `poweradmin/poweradmin` — affected >=4.3.0 <4.3.3

## Details
### Summary
Poweradmin v4.3.2 uses the attacker-controlled `HTTP_HOST` request header as the
  authoritative source for building callback URLs in its OIDC, SAML, and logout
  authentication flows without any validation. An unauthenticated attacker can poison
  the `redirect_uri` sent to the Identity Provider, causing the IdP to redirect the
  victim's authorization code to an attacker-controlled server - resulting in full
  account takeover with no credentials required.

  Three independent code paths are affected:

  - **Primary (Critical):** `OidcService::getCallbackUrl()` - `redirect_uri` poisoning
  - **Secondary (High):** `SamlConfigurationService::getBaseUrl()` - SAML ACS/SLO URL poisoning
  - **Tertiary (Medium):** `LogoutController::getBaseUrl()` - post-logout redirect poisoning

### Details

***Root Cause***

  The application constructs absolute URLs dynamically from `HTTP_HOST` rather than
  from a trusted configured base URL. The header is fully client-controlled and is not
  validated before use in any authentication flow.

  Poweradmin's own codebase contains the correct pattern -
  `DocsController::getValidatedHost()` (line 244) calls `isValidHostname()` before
  using the value - but this was never applied to authentication flows.

  ### Primary: `lib/Application/Service/OidcService.php` (~line 460)

  ```php
  private function getCallbackUrl(): string
  {
      $scheme = $this->detectScheme();
      // HTTP_HOST taken directly with zero validation
      $host = $this->request->getServerParam('HTTP_HOST', 'localhost');
      $basePrefix = $this->configManager->get('interface', 'base_url_prefix', '');
      return $scheme . '://' . $host . $basePrefix . '/oidc/callback';
  }

  HTTP_HOST is embedded verbatim as redirect_uri in the OAuth 2.0 authorization
  request sent to the IdP. HTTP_X_FORWARDED_PROTO is similarly used unvalidated
  for scheme detection.

  Secondary: lib/Application/Service/SamlConfigurationService.php (~line 134)

  private function getBaseUrl(): string
  {
      $configuredBaseUrl = $this->configManager->get('interface', 'base_url', '');
      if (!empty($configuredBaseUrl)) {
          return rtrim($configuredBaseUrl, '/');  // safe path - rarely configured
      }
      // Falls through on every default installation
      $host = $_SERVER['HTTP_HOST'] ?? 'localhost';
      ...
      return $scheme . '://' . $host . $prefix;
  }

  Used to construct SAML ACS URL, SLO URL, and entity ID - all poisonable via Host header.
  The safe fallback only activates when interface.base_url is explicitly set, which is
  optional and empty by default.

  Tertiary: lib/Application/Controller/LogoutController.php (~line 272)

  Same $_SERVER['HTTP_HOST'] pattern used for post-logout redirect URL construction.

### PoC
Environment: Poweradmin v4.3.2, Docker, PHP 8.2, OIDC enabled, interface.base_url empty (default).

  docker exec poweradmin-container php -r "
  require '/app/vendor/autoload.php';
  putenv('PA_CONFIG_PATH=/app/config/settings.php');

  use PowerAdmin\Application\Service\OidcService;
  use PowerAdmin\Infrastructure\Configuration\ConfigurationManager;
  use PowerAdmin\Infrastructure\Web\Request;

  \$_SERVER['HTTP_HOST'] = 'attacker.com';
  \$_SERVER['HTTPS']     = '';

  \$config      = ConfigurationManager::getInstance();
  \$request     = new Request();
  \$oidcService = new OidcService(\$config, \$request);
  \$authUrl     = \$oidcService->initiateAuthFlow('test');

  parse_str(parse_url(\$authUrl, PHP_URL_QUERY), \$p);
  echo 'redirect_uri: ' . urldecode(\$p['redirect_uri']) . PHP_EOL;

  if (str_contains(\$p['redirect_uri'], 'attacker.com')) {
      echo '[CONFIRMED] Host header injection successful' . PHP_EOL;
  }
  "

  Output:

  redirect_uri: http://attacker.com/oidc/callback

  [CONFIRMED] Host header injection successful - redirect_uri contains attacker.com

  The redirect_uri in the authorization request sent to the Identity Provider is
  http://attacker.com/oidc/callback. The victim's authorization code will be
  delivered to this URL upon successful authentication.

  Note on PKCE: PKCE does not mitigate this attack. The attacker initiates the
  flow themselves and controls both code_challenge and code_verifier.

### Impact
Direct Impact

  An attacker who can send a request with a spoofed Host header - directly or via a
  misconfigured reverse proxy (proxy_set_header Host $http_host is the nginx default) -
  can steal any user's authorization code and gain full authenticated access to Poweradmin.
  No credentials, malware, or prior access required.

  DNS Infrastructure Impact

  Poweradmin manages PowerDNS. A compromised administrator account grants full DNS zone
  control, enabling:

  - MX hijacking - redirect all inbound email to attacker's mail server; intercept
  password reset emails and 2FA codes for any third-party service registered with the domain
  - SPF/DKIM manipulation - add attacker's IP to SPF, publish attacker's DKIM key →
  send cryptographically authenticated email as the organization (passes DMARC)
  - Subdomain takeover - point mail., vpn., app. to attacker infrastructure
  - SSL certificate theft - remove CAA records and complete ACME DNS-01 challenge
  to obtain wildcard certificate *.company.com from any CA
  - Full domain delegation - delegate subdomains to attacker nameserver

  CVSS v3.1

  ┌──────────────────────────────────┬─────────────────────────────────────┬──────────────┐
  │             Scenario             │               Vector                │    Score     │
  ├──────────────────────────────────┼─────────────────────────────────────┼──────────────┤
  │ Standard deployment              │ AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:L │ 8.2 High     │
  ├──────────────────────────────────┼─────────────────────────────────────┼──────────────┤
  │ Proxy misconfigured ($http_host) │ AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:L │ 9.3 Critical │
  └──────────────────────────────────┴─────────────────────────────────────┴──────────────┘

  Recommended Fix

  Immediate mitigation: Set interface.base_url in config/settings.php -
  activates the safe branch in SamlConfigurationService immediately.

  Code fix for OidcService: Prefer the configured base URL; if absent, validate
  HTTP_HOST via filter_var($hostname, FILTER_VALIDATE_DOMAIN, FILTER_FLAG_HOSTNAME)
  before use - the same pattern already implemented in DocsController::getValidatedHost().

## References
- https://github.com/poweradmin/poweradmin/security/advisories/GHSA-3735-5339-xfwx
- https://nvd.nist.gov/vuln/detail/CVE-2026-54588
- https://github.com/poweradmin/poweradmin
- https://github.com/poweradmin/poweradmin/releases/tag/v4.2.4
- https://github.com/poweradmin/poweradmin/releases/tag/v4.3.3
