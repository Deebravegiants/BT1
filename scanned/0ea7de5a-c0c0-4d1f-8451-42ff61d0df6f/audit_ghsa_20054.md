# [M] HAProxyMessageDecoder Stack Exhaustion DoS

## Summary
Severity: Medium
Advisory: GHSA-fx2c-96vj-985v
CVE: CVE-2022-41881
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-12-12
Source: https://github.com/advisories/GHSA-fx2c-96vj-985v
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-haproxy` — affected >=0 <4.1.86.Final

## Details
### Impact
A StackOverflowError can be raised when parsing a malformed crafted message due to an infinite recursion.

### Patches
Users should upgrade to 4.1.86.Final.

### Workarounds
There is no workaround, except using a custom HaProxyMessageDecoder.

### References
When parsing a TLV with type = PP2_TYPE_SSL, the value can be again a TLV with type = PP2_TYPE_SSL and so on.
The only limitation of the recursion is that the TLV length cannot be bigger than 0xffff because it is encoded in an unsigned short type.
Providing a TLV with a nesting level that is large enough will lead to raising of a StackOverflowError.
The StackOverflowError will be caught if HAProxyMessageDecoder is used as part of Netty’s ChannelPipeline, but using it directly without the ChannelPipeline will lead to a thrown exception / crash.


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [netty](https://github.com/netty/netty)

## References
- https://github.com/netty/netty/security/advisories/GHSA-fx2c-96vj-985v
- https://nvd.nist.gov/vuln/detail/CVE-2022-41881
- https://github.com/netty/netty
- https://lists.debian.org/debian-lts-announce/2023/01/msg00008.html
- https://security.netapp.com/advisory/ntap-20230113-0004
- https://www.debian.org/security/2023/dsa-5316
