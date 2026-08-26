# [M] CVE-2026-9079: stale proxy password leak

## Summary
Severity: Medium
Program: curl
Weakness: Information Disclosure
Reporter: keen4n
State: resolved
Disclosed: 2026-06-24T08:26:56.851Z
CVE: CVE-2026-9079
Source: https://hackerone.com/reports/3750295

## Details
#### Product

Product name: curl / libcurl

Product link: https://github.com/curl/curl

Suggested CWE: CWE-226: Sensitive Information in Resource Not Removed Before Reuse (https://cwe.mitre.org/data/definitions/226.html); alternative CWE-200: Exposure of Sensitive Information to an Unauthorized Actor (https://cwe.mitre.org/data/definitions/200.html)

Affected versions: `8.8.0 <= libcurl <= 8.20.0` are confirmed affected. curl/libcurl `8.21.0-DEV`, commit `b2476a07128fc1e83a0b322fe6eb9dfa761db53d`, is also affected.

Unaffected versions: `libcurl <= 8.7.1` do not contain the `CURLOPT_PROXYUSERPWD` setter change that introduced this issue.

Introduced in: this issue was introduced by commit `d5e83eb745762f48d8fafadc5df5dd3ae8d8941e` (`url: do not URL decode proxy credentials`) in curl 8.8.0. This commit changed `CURLOPT_PROXYUSERPWD` from writing directly to the internal proxy username/password fields to first parsing the input into temporary `u` / `p` variables and then writing back only the components that exist.

Reference: https://github.com/curl/curl/commit/d5e83eb745762f48d8fafadc5df5dd3ae8d8941e


#### Summary

curl is a widely used command-line network transfer tool, and libcurl is the transfer library it provides for integration into other applications. libcurl provides the `CURLOPT_PROXYUSERPWD` option to set the `username:password` used for HTTP proxy authentication. The official documentation states that when this option is set multiple times, the last set string overrides the previous one, and setting this option to `NULL` disables its use.

However, the implementation of `CURLOPT_PROXYUSERPWD` has a stale-state issue. When the same easy handle is first configured with proxy credentials such as `victim:secret`, and later `CURLOPT_PROXYUSERPWD` is set to a username-only value such as `attacker`, or set to `NULL` in an attempt to clear the credentials, the old proxy password `secret` remains stored inside the handle. When a later request is sent through a proxy and proxy authentication is triggered, libcurl sends the old password to the proxy server, leaking a previous request's or previous task's proxy password to a later proxy.

This is a credential disclosure vulnerability. It primarily affects applications that reuse libcurl easy handles and allow tasks with different trust levels to configure proxy parameters, such as proxy pools, download services, crawler platforms, CI/automation systems, and other multi-tenant services built on libcurl.



#### Details

The official documentation describes the semantics of `CURLOPT_PROXYUSERPWD` as follows:

- This option sets the `[username]:[password]` to use for the connection to the HTTP proxy.
- When this option is set multiple times, the last set string overrides the previous ones.
- Setting this option to `NULL` disables its use.

Reference: https://curl.se/libcurl/c/CURLOPT_PROXYUSERPWD.html

The issue is in the setter logic for `CURLOPT_PROXYUSERPWD`. The option first parses the provided `username:password` string into temporary variables `u` and `p`, then URL-decodes those components and writes them to the internal proxy username and proxy password fields. The implementation replaces the internal username only when `u` is non-null, and replaces the internal password only when `p` is non-null:

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3750295_
