# [M] Improper Neutralization of CRLF Sequences in HTTP Headers ('HTTP Request/Response Splitting') in trillium-http and trillium-client

## Summary
Severity: Medium
Advisory: GHSA-9f9p-cp3c-72jf
CVE: CVE-2024-23644
CWE: CWE-113, CWE-436
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-9f9p-cp3c-72jf
Type: github-advisory

## Affected
- crates.io: `trillium-http` — affected >=0 <0.3.12
- crates.io: `trillium-client` — affected >=0 <0.5.4

## Details
### Summary
Insufficient validation of outbound header values may lead to request splitting or response splitting attacks in scenarios where attackers have sufficient control over outbound headers.

### Details
Outbound `trillium_http::HeaderValue` and `trillium_http::HeaderName` can be constructed infallibly and were not checked for illegal bytes when sending requests from the client or responses from the server. Thus, if an attacker has sufficient control over header values (or names) in a request or response that they could inject `\r\n` sequences, they could get the client and server out of sync, and then pivot to gain control over other parts of requests or responses. (i.e. exfiltrating data from other requests, SSRF, etc.)

### Patches

#### trillium-http >= 0.3.12:
* If a header name is invalid in server response headers, the specific header and any associated values are omitted from network transmission.
* If a header value is invalid in server response headers, the individual header value is omitted from network transmission. Other headers values with the same header name will still be sent.

#### trillium-client >= 0.5.4:
* If any header name or header value is invalid in the client request headers, awaiting the client Conn returns an `Error::MalformedHeader` prior to any network access.

### Workarounds

trillium services and client applications should sanitize or validate untrusted input that is included in header values and header names. Carriage return, newline, and null characters are not allowed.

### Impact

This only affects use cases where attackers have control of outbound headers, and can insert "\r\n" sequences. Specifically, if untrusted and unvalidated input is inserted into header names or values.

### A note on timing from @jbr on behalf of `trillium-rs`

@divergentdave filed this vulnerability many months ago but I did not see it until the evening of Jan 23, 2024. Patches were issued less than 24h after reading the vulnerability. The [security policy](https://github.com/trillium-rs/trillium/blob/main/SECURITY.md) has been [updated](https://github.com/trillium-rs/trillium/commit/b27950ceae52aa7a0f482494fe67b6069234d417) to avoid delays like this in the future.

## References
- https://github.com/trillium-rs/trillium/security/advisories/GHSA-9f9p-cp3c-72jf
- https://nvd.nist.gov/vuln/detail/CVE-2024-23644
- https://github.com/trillium-rs/trillium/commit/16a42b3f8378a3fa4e61ece3e3e37e6a530df51d
- https://github.com/trillium-rs/trillium/commit/8d468f85e27b8d0943d6f43ce9f8c7397141a999
- https://github.com/trillium-rs/trillium
- https://rustsec.org/advisories/RUSTSEC-2024-0008.html
- https://rustsec.org/advisories/RUSTSEC-2024-0009.html
