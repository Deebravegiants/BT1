# [M] github.com/lestrrat-go/jwx vulnerable to Potential Padding Oracle Attack

## Summary
Severity: Medium
Advisory: GHSA-rm8v-mxj3-5rmq
Ecosystem: Go
Published: 2023-06-14
Source: https://github.com/advisories/GHSA-rm8v-mxj3-5rmq
Type: github-advisory

## Affected
- Go: `github.com/lestrrat-go/jwx/v2` — affected >=0 <2.0.11
- Go: `github.com/lestrrat-go/jwx` — affected >=0 <1.2.26

## Details
### Summary

Decrypting AES-CBC encrypted JWE has Potential Padding Oracle Attack Vulnerability.

### Details

On [v2.0.10](https://github.com/lestrrat-go/jwx/releases/tag/v2.0.10), decrypting AES-CBC encrypted JWE may return an error "failed to generate plaintext from decrypted blocks: invalid padding":

https://github.com/lestrrat-go/jwx/blob/8840ffd4afc5839f591ff0e9ba9034af52b1643e/jwe/internal/aescbc/aescbc.go#L210-L213

Reporting padding error causes [Padding Oracle Attack](https://en.wikipedia.org/wiki/Padding_oracle_attack) Vulnerability.
RFC 7516 JSON Web Encryption (JWE) says that we **MUST NOT** do this.

> 11.5.  Timing Attacks
> To mitigate the attacks described in RFC 3218 [RFC3218], the
> recipient MUST NOT distinguish between format, padding, and length
> errors of encrypted keys.  It is strongly recommended, in the event
> of receiving an improperly formatted key, that the recipient
> substitute a randomly generated CEK and proceed to the next step, to
> mitigate timing attacks.

In addition, the time to remove padding depends on the length of the padding.
It may leak the length of the padding by Timing Attacks.

https://github.com/lestrrat-go/jwx/blob/796b2a9101cf7e7cb66455e4d97f3c158ee10904/jwe/internal/aescbc/aescbc.go#L33-L66

To mitigate Timing Attacks, it MUST be done in constant time.

### Impact

The authentication tag is verified, so it is not an immediate attack.

## References
- https://github.com/lestrrat-go/jwx/security/advisories/GHSA-rm8v-mxj3-5rmq
- https://github.com/lestrrat-go/jwx/commit/6c41e3822485fc7e11dd70b4b0524b075d66b103
- https://github.com/lestrrat-go/jwx/commit/d9ddbc8e5009cfdd8c28413390b67afa7f576dd6
- https://github.com/lestrrat-go/jwx
- https://github.com/lestrrat-go/jwx/blob/796b2a9101cf7e7cb66455e4d97f3c158ee10904/jwe/internal/aescbc/aescbc.go#L33-L66
- https://github.com/lestrrat-go/jwx/blob/8840ffd4afc5839f591ff0e9ba9034af52b1643e/jwe/internal/aescbc/aescbc.go#L210-L213
