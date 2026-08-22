# [M] CVE-2026-8927: env-set cross-proxy Digest auth state leak

## Summary
Severity: Medium
Program: curl
Weakness: Improper Authentication - Generic
Reporter: adyej
State: resolved
Disclosed: 2026-06-24T08:24:47.684Z
CVE: CVE-2026-8927, CVE-2026-7168
Source: https://hackerone.com/reports/3744543

## Details
## AI-assisted preparation note

I used AI assistance to help structure and format this report, but the technical findings, PoC, and verification results are based on local testing against curl/libcurl 8.20.0.

## Summary

I found a possible incomplete-fix variant of CVE-2026-7168 in libcurl 8.20.0.

The original issue involved stale Digest proxy authentication state being sent from `proxyA` to `proxyB` when the same libcurl easy handle was reused after changing proxies. In curl 8.20.0, the explicit `CURLOPT_PROXY` path appears to be fixed: changing the proxy via `CURLOPT_PROXY` clears the old proxy Digest/auth state correctly.

However, I found that the same cleanup does not appear to happen when the effective proxy changes through environment variables such as `http_proxy` or `ALL_PROXY`.

As a result, when the same easy handle is reused:

1. The first transfer uses `proxyA` from `http_proxy` and authenticates with HTTP Digest proxy authentication.
2. The environment variable is changed so the next transfer uses `proxyB`.
3. The same easy handle performs the second transfer.
4. `proxyB` receives a `Proxy-Authorization: Digest` header using stale Digest state from `proxyA`.

This was reproduced against official curl/libcurl 8.20.0.

## Affected version

Tested against official curl/libcurl 8.20.0.

The PoC confirms:

```text
LIBCURL_RUNTIME=8.20.0
LIBCURL_HEADERS=8.20.0
```

## Impact

A malicious second proxy can receive a `Proxy-Authorization: Digest` header generated from the previous proxy's Digest challenge state.

In my replay test, the header captured by `proxyB` was valid for `proxyA` and could be replayed successfully. This is the same security class as CVE-2026-7168: proxy authentication state intended for one proxy crosses a proxy boundary and is exposed to another proxy.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/3744543_
