# [M] Nuxt dev server discloses project root and workspace UUID via the Chrome DevTools workspace endpoint

## Summary
Severity: Medium
Advisory: GHSA-7c4v-fwgw-9rf7
CVE: CVE-2026-72744
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:4.0/AV:A/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-07
Source: https://github.com/advisories/GHSA-7c4v-fwgw-9rf7
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.4.7 <4.5.1
- npm: `nuxt` — affected >=3.21.7 <3.21.10

## Details
### Impact

When a Nuxt dev server is bound to a network-reachable interface (for example `nuxt dev --host` for on-device testing), the default-enabled Chrome DevTools workspace endpoint `GET /.well-known/appspecific/com.chrome.devtools.json` returns the absolute project root (`workspace.root`, i.e. `rootDir`) and a persistent per-project workspace UUID.

`GHSA-rq7w-g337-39qq` added a gate (`isLocalDevRequest`) intended to restrict this endpoint to local requests, but that gate is header-based: it trusts request metadata rather than the connected peer address. A request with no `Sec-Fetch-Site`, `Origin`, and `Referer` headers (normal for a non-browser client such as `curl`) is treated as local, and the `Host` allow-list is compared against the attacker-supplied `Host` header. As a result, any unauthenticated host that can reach the dev server on the LAN can retrieve the project's absolute filesystem path and workspace UUID, for example with `curl -H 'Host: localhost' http://<dev-host-lan-ip>:3000/.well-known/appspecific/com.chrome.devtools.json`.

This is information disclosure only: there is no file read, file write, or code execution reachable from the endpoint. It requires the dev server to be reachable beyond loopback and `experimental.chromeDevtoolsProjectSettings` to be enabled (it defaults to `true`). Production builds are unaffected, because the endpoint is registered only as a development handler.

### Patches

Fixed in `nuxt@4.5.1` and `nuxt@3.21.10`. The endpoint now additionally requires the connected TCP peer to be a loopback address, verified from the socket rather than from request headers, so a non-loopback LAN client is rejected regardless of the `Host`, `Origin`, `Referer`, or `Sec-Fetch-*` headers it sends. The shared header-based check is left unchanged, so the CSRF / same-origin behaviour that other dev handlers rely on is preserved. After this fix, Chrome DevTools workspace auto-mapping only works when the browser reaches the dev server over loopback (`localhost` / `127.0.0.1` / `::1`), which matches the feature's intent (the browser and dev server sharing a filesystem).

### Workarounds

- Do not bind the dev server to a non-loopback interface on an untrusted network, or restrict access to the dev port with a firewall.
- Disable the feature by setting `experimental.chromeDevtoolsProjectSettings: false` in `nuxt.config`.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-7c4v-fwgw-9rf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-72744
- https://github.com/nuxt/nuxt/commit/00f71bb6517abff67257c8ea1fcdc777b938b68d
- https://github.com/nuxt/nuxt/commit/e30c611ea03240f341fe784ab1711aa6424da2fa
- https://github.com/nuxt/nuxt
- https://github.com/nuxt/nuxt/releases/tag/v3.21.10
- https://github.com/nuxt/nuxt/releases/tag/v4.5.1
- https://www.vulncheck.com/advisories/nuxt-before-information-disclosure-via-chrome-devtools
