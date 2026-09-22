# [M] Netty vulnerable to HTTP Response splitting from assigning header value iterator

## Summary
Severity: Medium
Advisory: GHSA-hh82-3pmq-7frp
CVE: CVE-2022-41915
CWE: CWE-113, CWE-436
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-hh82-3pmq-7frp
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.1.83.Final <4.1.86.Final

## Details
### Impact
When calling `DefaultHttpHeaders.set` with an _iterator_ of values (as opposed to a single given value), header value validation was not performed, allowing malicious header values in the iterator to perform [HTTP Response Splitting](https://owasp.org/www-community/attacks/HTTP_Response_Splitting).

### Patches
The necessary validation was added in Netty 4.1.86.Final.

### Workarounds
Integrators can work around the issue by changing the `DefaultHttpHeaders.set(CharSequence, Iterator<?>)` call, into a `remove()` call, and call `add()` in a loop over the iterator of values.

### References
[HTTP Response Splitting](https://owasp.org/www-community/attacks/HTTP_Response_Splitting)
[CWE-113: Improper Neutralization of CRLF Sequences in HTTP Headers](https://cwe.mitre.org/data/definitions/113.html)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [[example link to repo](https://github.com/netty/netty)](https://github.com/netty/netty)
* Email us at [netty-security@googlegroups.com](mailto:netty-security@googlegroups.com)

## References
- https://github.com/netty/netty/security/advisories/GHSA-hh82-3pmq-7frp
- https://nvd.nist.gov/vuln/detail/CVE-2022-41915
- https://github.com/netty/netty/issues/13084
- https://github.com/netty/netty/pull/12760
- https://github.com/netty/netty/commit/c37c637f096e7be3dffd36edee3455c8e90cb1b0
- https://github.com/netty/netty/commit/fe18adff1c2b333acb135ab779a3b9ba3295a1c4
- https://github.com/netty/netty
- https://lists.debian.org/debian-lts-announce/2023/01/msg00008.html
- https://security.netapp.com/advisory/ntap-20230113-0004
- https://www.debian.org/security/2023/dsa-5316
