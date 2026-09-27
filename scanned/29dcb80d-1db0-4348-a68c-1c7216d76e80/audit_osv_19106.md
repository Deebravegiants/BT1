# [H] CVE-2020-7662

## Summary
Severity: High
Advisory: CVE-2020-7662
Aliases: GHSA-g78m-2chm-r7qv, SNYK-JS-WEBSOCKETEXTENSIONS-570623
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-02
Source: https://osv.dev/vulnerability/CVE-2020-7662
Type: osv

## Details
websocket-extensions npm module prior to 0.1.4 allows Denial of Service (DoS) via Regex Backtracking. The extension parser may take quadratic time when parsing a header containing an unclosed string parameter value whose content is a repeating two-byte sequence of a backslash and some other character. This could be abused by an attacker to conduct Regex Denial Of Service (ReDoS) on a single-threaded server by providing a malicious payload with the Sec-WebSocket-Extensions header.

## References
- https://github.com/faye/websocket-extensions-node/commit/29496f6838bfadfe5a2f85dff33ed0ba33873237
- https://blog.jcoglan.com/2020/06/02/redos-vulnerability-in-websocket-extensions
- https://github.com/faye/websocket-extensions-node/security/advisories/GHSA-g78m-2chm-r7qv
- https://snyk.io/vuln/SNYK-JS-WEBSOCKETEXTENSIONS-570623
