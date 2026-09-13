# [H] fastify-bearer-auth vulnerable to Timing Attack Vector

## Summary
Severity: High
Advisory: GHSA-376v-xgjx-7mfr
CVE: CVE-2022-31142
CWE: CWE-203, CWE-208
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-376v-xgjx-7mfr
Type: github-advisory

## Affected
- npm: `fastify-bearer-auth` — affected >=5.0.1
- npm: `@fastify/bearer-auth` — affected >=0 <7.0.2
- npm: `@fastify/bearer-auth` — affected >=8.0.0 <8.0.1

## Details
### Impact

fastify-bearer-auth does not securely use crypto.timingSafeEqual. A malicious attacker could estimate the length of one valid bearer token. According to the corresponding RFC 6750, the bearer token has only base64 valid characters, reducing the range of characters for a brute force attack.

All versions of fastify-bearer-auth are also affected.

### Patches

We released:

* v8.0.1 with a fix for the Fastify v4 line
* v7.0.2 with a fix for the Fastify v3 line

### Workarounds

There are no workarounds. Update your dependencies.

### References

https://hackerone.com/reports/1633287

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/fastify/fastify-bearer-auth](https://github.com/fastify/fastify-bearer-auth)
* Email us at [hello@matteocollina.com](mailto:hello@matteocollina.com)

## References
- https://github.com/fastify/fastify-bearer-auth/security/advisories/GHSA-376v-xgjx-7mfr
- https://nvd.nist.gov/vuln/detail/CVE-2022-31142
- https://github.com/fastify/fastify-bearer-auth/commit/0c468a616d7e56126dc468150f6a5a92e530b8e4
- https://github.com/fastify/fastify-bearer-auth/commit/39353b15409ee99474545f615ffb16180cf3b716
- https://github.com/fastify/fastify-bearer-auth/commit/f921a0582dc83112039004a9b5041141b50c5b3f
- https://hackerone.com/reports/1633287
- https://github.com/fastify/fastify-bearer-auth
