# [M] Netty susceptible to HTTP/2 Reset Attack with different on-the-wire signature

## Summary
Severity: Medium
Advisory: GHSA-563q-j3cm-6jxm
CVE: CVE-2026-50560
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-563q-j3cm-6jxm
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http2` — affected >=4.2.0.Final <4.2.15.Final
- Maven: `io.netty:netty-codec-http2` — affected >=0 <4.1.135.Final

## Details
### Summary

Netty HTTP/2 max header size handling produces attack similar to HTTP/2 Rapid Reset.

### Details

There is a setting in the http2 specification called `SETTINGS_MAX_HEADER_LIST_SIZE`. According to[ the RFC](https://www.rfc-editor.org/rfc/rfc9113.html#name-defined-settings): “This advisory setting informs a peer of the maximum field section size that the sender is prepared to accept, in units of octets.”

When a client sends that setting to Netty, it appears that Netty will behave as follows:

- Read the request
- Proxy the request to the origin
- Attempt to produce a response
- Create an exception while writing the headers for the response

Functionally, this should be similar to the http2 reset attack, but with a different on-the-wire signature.

## Remediation

When speaking with clients, Netty should potentially treat this as “advisory” and ignore it.  It would be best to ignore the SETTINGS_MAX_HEADER_LIST_SIZE setting from clients (or ignore it when sending to clients). According to the spec, a server does not need to honor this advisory setting, and it appears that other http/2 implementations ignore it when acting as a server.

### Impact

This is a DDoS attack similar to the HTTP/2 Rapid Reset Attack.

## Credit
Jonathan Looney (Engineering, Netflix)

## Contact
Ashley Tolbert (Security, Netflix) - artolbert@netflix.com

## References
- https://github.com/netty/netty/security/advisories/GHSA-563q-j3cm-6jxm
- https://nvd.nist.gov/vuln/detail/CVE-2026-50560
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.135.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.15.Final
- https://www.rfc-editor.org/rfc/rfc9113.html#name-defined-settings
