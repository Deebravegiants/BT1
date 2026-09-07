# [M] The Thinbus Javascript Secure Remote Password (SRP) Client Generates Fewer Bits of Entropy Than Intended

## Summary
Severity: Medium
Advisory: GHSA-8q6v-474h-whgg
CVE: CVE-2025-54885
CWE: CWE-331
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2025-08-06
Source: https://github.com/advisories/GHSA-8q6v-474h-whgg
Type: github-advisory

## Affected
- npm: `thinbus-srp` — affected >=0 <2.0.1

## Details
### Impact
A protocol compliance bug in thinbus-srp-npm versions prior to 2.0.1 causes the client to generate a fixed 252 bits of entropy instead of the intended bit length of the safe prime (defaulted to 2048 bits). RFC 5054 states in section [2.5.4 Client Key Exchange ](https://datatracker.ietf.org/doc/html/rfc5054#section-2.5.4)

> The client key exchange message carries the client's public value
   (A).  The client calculates this value as A = g^a % N, where a is a
   random number that SHOULD be at least 256 bits in length.

The client public value is being generated from a private value that is 4 bits below the specification. This reduces the protocol's designed security margin it is now practically exploitable. The servers full sized 2048 bit random number is used to create the shared session key and password proof. 

### Patches

The issue is fixed in versions >= 2.0.1

### Workarounds

It is possible to patch a legacy version: 

```javascript
// WRONG
var hexLength = this.toHex(N).length;

// CORRECT  
var hexLength = this.toHex(this.N()).length;
```

## References
- https://github.com/simbo1905/thinbus-srp-npm/security/advisories/GHSA-8q6v-474h-whgg
- https://nvd.nist.gov/vuln/detail/CVE-2025-54885
- https://github.com/simbo1905/thinbus-srp-npm/issues/28
- https://github.com/simbo1905/thinbus-srp-npm/pull/30/commits/4aeaea2366e090765a8204059c7bcf3616438d31
- https://github.com/simbo1905/thinbus-srp-npm/commit/aa7064c1db7294ce867e9bc92f26fa6c71a5a2cb
- https://github.com/simbo1905/thinbus-srp-npm
