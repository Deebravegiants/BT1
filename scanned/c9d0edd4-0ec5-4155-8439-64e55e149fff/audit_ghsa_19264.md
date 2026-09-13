# [M] @misskey-dev/summaly allows IP Filter Bypass via Redirect

## Summary
Severity: Medium
Advisory: GHSA-jqx4-9gpq-rppm
CWE: CWE-346
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-05-06
Source: https://github.com/advisories/GHSA-jqx4-9gpq-rppm
Type: github-advisory

## Affected
- npm: `@misskey-dev/summaly` — affected >=5.1.0 <5.2.1

## Details
### Summary
Due to a validation error in `got.scpaping`, it is possible to use an HTTP redirect to avoid IP filtering.

### Details
In `got.scpaping`, Summaly first makes a HTTP `HEAD` request to the page being summarized. It then preforms private IP address checks on the `HEAD` response, then makes an additional HTTP `GET` request to the page being summarized. Unfortunately, since private IP address checks aren't performed on the `GET` response, the `GET` response can issue a HTTP redirect to a private IP address, which will succeed, regardless of if private IP addresses are allowed by Summaly.

### PoC
With a simple Caddy webserver, you can get Summaly to summarize a page hosted via a local IP address:
```caddy
@summaly-bypass-head {
    method HEAD
    path /summaly-bypass
}
@summaly-bypass-get {
    method GET
    path /summaly-bypass
}
header @summaly-bypass-head Content-Type "text/html"
respond @summaly-bypass-head 200
redir @summaly-bypass-get http://127.0.0.1:3080/
```

### Impact
Using this bypass, an attacker can probe a victims internal network for HTTP services that aren't supposed to be exposed to the outside world. While they might only have read-only access through this, it may still be possible to extract sensitive information or be used to probe a network prior to attacking via other exploits without leaving a trace.

## References
- https://github.com/misskey-dev/summaly/security/advisories/GHSA-jqx4-9gpq-rppm
- https://github.com/misskey-dev/summaly/commit/dfe6451012aac42eabe71d4ed721d8058c4066b4
- https://github.com/misskey-dev/summaly
