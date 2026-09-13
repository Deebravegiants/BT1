# [H] NukeViet: Pre-authentication SSRF via X-Forwarded-Host

## Summary
Severity: High
Advisory: GHSA-4chg-4752-w88r
CVE: CVE-2026-55372
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-4chg-4752-w88r
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=0 <4.6.00

## Details
## Summary

An unauthenticated attacker can coerce the server into issuing HTTP requests to an attacker-chosen host by spoofing the `X Forwarded-Host` (and `X-Forwarded-Proto`) request headers. The forwarded host is used, without validation, to build the URL that `server_info_update()` fetches with cURL, resulting in a Server-Side Request Forgery (SSRF) that requires no authentication.

## Affected component

- File: `includes/ini.php` — function `server_info_update()` (cURL sink)
- File: `vendor/vinades/nukeviet/Core/Server.php` — `standardizeHost()` and the forwarded-header handling in the constructor (source of the tainted host)
- Trigger: `POST` request containing the field `__serverInfoUpdate=1`, handled early in `includes/ini.php` before any authentication.

## Details

`NukeViet\Core\Server` derives `original_host` / `original_protocol` from the `X-Forwarded-Host` / `X-Forwarded-Proto` headers and exposes them via `getOriginalHost()` / `getOriginalProtocol()`. These values are attacker-controlled and were not validated against the site's configured domains (`my_domains`).

In `server_info_update()` the tainted host and scheme are concatenated directly into a cURL URL:

```php
$proto = $nv_Server->getOriginalProtocol();   // from X-Forwarded-Proto
$host  = $nv_Server->getOriginalHost();        // from X-Forwarded-Host
$ch = curl_init($proto . '://' . $host . NV_BASE_SITEURL . 'index.php?response_headers_detect=1');
curl_exec($ch);
```

Two factors made this reliably reachable:

1. The `__serverInfoUpdate` handler runs very early in `includes/ini.php`, before authentication, so the sink is reachable pre-auth.
2. The host sanitiser `standardizeHost()` stripped a trailing port only with the regex `(\:[0-9]+)$`, which is bypassed by appending a slash (e.g. `127.0.0.1:8081/`): the string no longer ends in `:digits`, so the port survives and an arbitrary `host:port` reaches the cURL call.

## Proof of Concept

```http
POST /index.php HTTP/1.1
Host: <victim>
X-Forwarded-Proto: http
X-Forwarded-Host: <attacker-controlled-host>:<port>/
Content-Type: application/x-www-form-urlencoded
Content-Length: 20

__serverInfoUpdate=1
```

The server then issues a request to the attacker-supplied host, confirmed via an out-of-band interaction (DNS + HTTP) on a collaborator endpoint.

## Impact

The SSRF is **blind**, **HEAD-only**, and uses a **fixed request path** (`…/index.php?response_headers_detect=1`):

- The fetched response is stored server-side in the `config_ini` cache and is **not reflected** to the attacker, so internal data cannot be exfiltrated directly.
- Because the path is fixed and not attacker-controlled, cloud metadata endpoints (e.g. `169.254.169.254/latest/meta-data/...`) cannot be reached, and `gopher://` / `dict://` request smuggling cannot inject arbitrary payloads.

What an attacker **can** do: unauthenticated internal host/port discovery (connection success/timing, with the port reachable through the regex bypass), and poisoning of the cached `server_headers` (the SSRF target's response headers are stored and applied to the site).

## Severity

Rated **High** rather than Critical, because the blind + fixed-path + HEAD design of the sink prevents data exfiltration, cloud credential theft, and internal RCE.

- CVSS v3.1 Base Score: **7.2 (High)**
- Vector: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N`

## Weakness

- Primary: **CWE-918: Server-Side Request Forgery (SSRF)**
- Contributing: CWE-20 (Improper Input Validation), CWE-644 (Improper Neutralization of HTTP Headers used by downstream components / trusting `X-Forwarded-*`).

## Remediation

Fixed by validating and normalising the forwarded values at the source and gating the request before the sink:

- `standardizeHost()` now extracts the host with `parse_url()` (defeats the `:port/` bypass) and lower-cases it.
- `X-Forwarded-Proto` is restricted to a `{http, https}` allow-list and falls back to the real server protocol otherwise.
- `X-Forwarded-Port` is validated as numeric and within range.
- The incoming host is checked against `my_domains` before `includes/ini.php` is reached; non-matching hosts are rejected/redirected, and `server_info_update()` additionally re-validates its target host against `my_domains` (defense in depth).

## Workaround

Configure the reverse proxy / web server to strip or override client-supplied `X-Forwarded-Host`, `X-Forwarded-Proto`, and `X-Forwarded-Port` headers, and ensure `my_domains` is configured with the site's canonical domain(s).

## References
- https://github.com/nukeviet/nukeviet/security/advisories/GHSA-4chg-4752-w88r
- https://github.com/nukeviet/nukeviet
