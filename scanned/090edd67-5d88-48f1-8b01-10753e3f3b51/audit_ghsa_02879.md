# [H] Insecure random number generation in keypair

## Summary
Severity: High
Advisory: GHSA-3f99-hvg4-qjwj
CVE: CVE-2021-41117
CWE: CWE-335
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-10-11
Source: https://github.com/advisories/GHSA-3f99-hvg4-qjwj
Type: github-advisory

## Affected
- npm: `keypair` — affected >=0 <1.0.4

## Details
## Description and Impact

A bug in the pseudo-random number generator used by [keypair](https://github.com/juliangruber/keypair) versions up to and including 1.0.3 could allow for weak RSA key generation. This could enable an attacker to decrypt confidential messages or gain authorized access to an account belonging to the victim. We recommend replacing any RSA keys that were generated using keypair version 1.0.3 or earlier.

## Fix

* The [bug](https://github.com/juliangruber/keypair/blob/87c62f255baa12c1ec4f98a91600f82af80be6db/index.js#L1008) in the pseudo-random number generator is fixed in commit [`9596418`](https://github.com/juliangruber/keypair/commit/9596418d3363d3e757676c0b6a8f2d35a9d1cb18).
* If the crypto module is available, it is used instead of the pseudo-random number generator. Also fixed in [`9596418`](https://github.com/juliangruber/keypair/commit/9596418d3363d3e757676c0b6a8f2d35a9d1cb18)

## Additional Details

The specific [line](https://github.com/juliangruber/keypair/blob/87c62f255baa12c1ec4f98a91600f82af80be6db/index.js#L1008) with the flaw is:

```javascript
b.putByte(String.fromCharCode(next & 0xFF))
```

The [definition](https://github.com/juliangruber/keypair/blob/87c62f255baa12c1ec4f98a91600f82af80be6db/index.js#L350-L352) of `putByte` is 

```javascript
util.ByteBuffer.prototype.putByte = function(b) {
  this.data += String.fromCharCode(b);
};
```

Simplified, this is `String.fromCharCode(String.fromCharCode(next & 0xFF))`. This results in most of the buffer containing zeros. An example generated buffer:

(Note: truncated for brevity)

```
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x00\x00\x00\x00\x04\x00\x00\x00....\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00
```

Since it is masking with 0xFF, approximately 97% of the bytes are converted to zeros. The impact is that each byte in the RNG seed has a 97% chance of being 0 due to incorrect conversion.

## Credit

This issue was reported to GitHub Security Lab by Ross Wheeler of Axosoft. It was discovered by Axosoft engineer Dan Suceava, who noticed that [keypair](https://github.com/juliangruber/keypair) was regularly generating duplicate RSA keys. GitHub security engineer [@vcsjones (Kevin Jones)](https://github.com/vcsjones) independently investigated the problem and identified the cause and source code location of the bug.

## References
- https://github.com/juliangruber/keypair/security/advisories/GHSA-3f99-hvg4-qjwj
- https://nvd.nist.gov/vuln/detail/CVE-2021-41117
- https://github.com/juliangruber/keypair/commit/9596418d3363d3e757676c0b6a8f2d35a9d1cb18
- https://github.com/juliangruber/keypair
- https://github.com/juliangruber/keypair/releases/tag/v1.0.4
- https://securitylab.github.com/advisories/GHSL-2021-1012-keypair
