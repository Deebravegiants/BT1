# [H] CC-Tweaked has an SSRF Protection Bypass with NAT64

## Summary
Severity: High
Advisory: GHSA-5jh9-2h63-pw4q
CVE: CVE-2026-47695
CWE: CWE-918
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-5jh9-2h63-pw4q
Type: github-advisory

## Affected
- Maven: `cc.tweaked:cc-tweaked-1.21-core` — affected >=0 <1.119.0
- Maven: `cc.tweaked:cc-tweaked-1.20.1-core` — affected >=0 <1.119.0
- Maven: `cc.tweaked:cc-tweaked-1.20.4-core` — affected >=0 <1.119.0
- Maven: `cc.tweaked:cc-tweaked-1.20.5-core` — affected >=0 <1.119.0
- Maven: `cc.tweaked:cc-tweaked-1.20.6-core` — affected >=0 <1.119.0
- Maven: `cc.tweaked:cc-tweaked-1.19.3-core` — affected >=0 <1.119.0
- Maven: `cc.tweaked:cc-tweaked-1.19.4-core` — affected >=0 <1.119.0
- Maven: `cc.tweaked:cc-tweaked-1.20-core` — affected >=0 <1.119.0

## Details
### Summary

CC-Tweaked's HTTP API (`http.request`, `http.websocket`) blocks requests to private network ranges to prevent server-side request forgery (SSRF). This protection can be bypassed on IPv6-capable servers using NAT64 well-known prefix addresses (`64:ff9b::/96`). An attacker who can execute Lua code can reach any internal IPv4 service that the filter is intended to block, by addressing it as `http://[64:ff9b::<ipv4-as-hex>]/` instead of its direct IPv4 address. This affects any CC-Tweaked deployment on a network with NAT64 routing — a configuration that is standard on AWS, GCP, and other cloud platforms when using IPv6-only subnets.

### Details

The IP filter in [`PrivatePattern.matches()` (AddressPredicate.java#L121–L130)](https://github.com/cc-tweaked/CC-Tweaked/blob/663ffed4337da0dc3d82ace1e813e3c78b4a8c99/projects/core/src/main/java/dan200/computercraft/core/apis/http/options/AddressPredicate.java#L121-L130) blocks private network ranges by calling Java's standard `InetAddress` classification methods:

```java
public boolean matches(InetAddress socketAddress) {
    return socketAddress.isAnyLocalAddress()
        || socketAddress.isLoopbackAddress()
        || socketAddress.isLinkLocalAddress()
        || socketAddress.isSiteLocalAddress()
        || socketAddress.isMulticastAddress()
        || isUniqueLocalAddress(socketAddress)
        || isCarrierGradeNatAddress(socketAddress)
        || additionalAddresses.contains(socketAddress);
}
```

When a NAT64 address such as `64:ff9b::c0a8:0101` (encoding `192.168.1.1`) is resolved via `new InetSocketAddress("64:ff9b::c0a8:0101", 80)`, Java returns an `Inet6Address`. Every method above returns `false` for this address — the `64:ff9b::/96` prefix is not recognised by any of Java's built-in classification methods. The address passes the filter and CC-Tweaked opens a connection.

On a network with a `64:ff9b::/96 → NAT Gateway` route, that connection is translated at the network level: the embedded IPv4 address is extracted and the packet is forwarded to `192.168.1.1:80`. The internal service receives a normal IPv4 TCP connection.

The existing 6to4 (`2002::/16`) mitigation in [`AddressRule.java#L74–L75`](https://github.com/cc-tweaked/CC-Tweaked/blob/663ffed4337da0dc3d82ace1e813e3c78b4a8c99/projects/core/src/main/java/dan200/computercraft/core/apis/http/options/AddressRule.java#L74-L75) does not cover the NAT64 prefix. No other check catches `64:ff9b::/96`.

### PoC

**Preconditions** (all three required):
1. The server running CC-Tweaked has an IPv6 address assigned
2. The network has a NAT Gateway (or equivalent)
3. The route table contains `64:ff9b::/96 → NAT Gateway` — the standard AWS/GCP configuration for IPv6-only subnets with outbound IPv4 access ([AWS documentation](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-nat64-dns64.html))

**Lua payload** (targets an internal service at `10.0.1.17:8888`):
```lua
-- 10.0.1.17 = 0x0a000111, expressed as NAT64: 64:ff9b::0a00:0111
local res = http.request("http://[64:ff9b::0a00:0111]:8888/")
if res then print(res.readAll()) end
```

**Conversion formula** — for any blocked IPv4 `a.b.c.d`, the bypass address is:
```
64:ff9b::<hex(a)><hex(b)>:<hex(c)><hex(d)>
```

### Impact

This is a server-side request forgery (SSRF) vulnerability. Any user able to execute Lua code on a CC-Tweaked computer — including players on a public server — can use it to send HTTP requests to internal IPv4 services that the HTTP filter is designed to block. On cloud-hosted servers (AWS, GCP, Azure) using IPv6-only subnets with NAT64, which is an [increasingly common configuration following AWS's February 2024 public IPv4 pricing change](https://aws.amazon.com/blogs/aws/new-aws-public-ipv4-address-charge-public-ip-insights/), this includes other instances in the VPC, internal databases, and cloud management APIs.

**Suggested fix:** add a check for the NAT64 well-known prefix in [`PrivatePattern.matches()`](https://github.com/cc-tweaked/CC-Tweaked/blob/663ffed4337da0dc3d82ace1e813e3c78b4a8c99/projects/core/src/main/java/dan200/computercraft/core/apis/http/options/AddressPredicate.java#L121-L130):

```java
|| isNAT64Address(socketAddress)

private boolean isNAT64Address(InetAddress address) {
    if (!(address instanceof Inet6Address)) return false;
    byte[] b = address.getAddress();
    // 64:ff9b::/96 — NAT64 well-known prefix (RFC 6052)
    return b[0] == 0x00 && b[1] == 0x64 &&
           b[2] == (byte) 0xff && b[3] == (byte) 0x9b &&
           b[4] == 0 && b[5] == 0 && b[6] == 0 && b[7] == 0 &&
           b[8] == 0 && b[9] == 0 && b[10] == 0 && b[11] == 0;
}
```

This vulnerability does not seem to work on servers running on modern versions of MacOS.

## References
- https://github.com/cc-tweaked/CC-Tweaked/security/advisories/GHSA-5jh9-2h63-pw4q
- https://github.com/cc-tweaked/CC-Tweaked
