# [C] Craft CMS: Blind SSRF and Arbitrary JavaScript Injection via Host Header Poisoning in actionResourceJs

## Summary
Severity: Critical
Advisory: GHSA-c55v-343g-5xff
CVE: CVE-2026-55791
CWE: CWE-346
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-c55v-343g-5xff
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.10
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.18

## Details
**1. Overview**

Craft CMS is vulnerable to Server-Side Request Forgery (SSRF) and Arbitrary JavaScript Injection through the `/actions/app/resource-js` endpoint. By exploiting the default permissive `trustedHosts` configuration, an attacker can poison the `Host` or `X-Forwarded-Host` header to manipulate the application’s `$baseUrl`. This bypasses the endpoint’s internal URL validation, forcing the backend Guzzle client to fetch a malicious payload from an attacker-controlled server and reflect it to the client with a `Content-Type: application/javascript` header.

**2. Vulnerability Mechanism (Root Cause)**
The vulnerability manifests when `assetManager.cacheSourcePaths` is set to `false`. The attack chain relies on three structural flaws and insecure defaults:

- **A. Default Proxy Trust (`trustedHosts`):** Craft’s default `GeneralConfig::$trustedHosts` is set to `['any']`. This allows an attacker to bypass front-end web server (Nginx/Apache) strict `Host` header validations by simply injecting an `X-Forwarded-Host` header. Yii2 will parse this and globally set `$baseUrl` to the attacker's domain.
- **B. Insecure HTTP Client (`actionResourceJs`):** In `AppController::actionResourceJs()`, the `str_starts_with($url, $baseUrl)` validation is bypassed because `$baseUrl` is already poisoned by the attacker. The core then uses `Craft::createGuzzleClient()->get($url)`. Unlike the GraphQL Asset fetcher, this Guzzle instance defaults to `ALLOW_REDIRECTS => true`.
- **C. Forced JS Content-Type:** The response fetched from the attacker's server is blindly returned to the user via `$this->asRaw()` with the header `Content-Type: application/javascript`.

**3. Attack Scenario & Impact (Proof of Exploitability)**
This endpoint acts as a proxy, taking remote, unverified content and serving it as valid JavaScript. While the direct SSRF allows for internal network probing, the most devastating impact occurs when caching layers are involved.

If the Craft CMS instance is behind a caching layer, this vulnerability leads directly to **Web Cache Poisoning**:

1. An unauthenticated attacker sends the poisoned request.
2. The caching layer caches the malicious JavaScript response for the legitimate `/actions/app/resource-js` URI.
3. When an authenticated Administrator logs into the Control Panel, their browser loads the poisoned cached JavaScript (**Stored XSS**).
4. The malicious script extracts `window.Craft.csrfTokenValue` and silently sends a POST request to `/admin/actions/plugins/install-plugin`, achieving **1-Click Remote Code Execution (RCE)** via Session Riding.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-c55v-343g-5xff
- https://github.com/craftcms/cms/pull/18559
- https://github.com/craftcms/cms
