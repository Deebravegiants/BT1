# [H] fastify vulnerable to denial of service via malicious Content-Type

## Summary
Severity: High
Advisory: GHSA-455w-c45v-86rg
CVE: CVE-2022-39288
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-11
Source: https://github.com/advisories/GHSA-455w-c45v-86rg
Type: github-advisory

## Affected
- npm: `fastify` — affected >=4.0.0 <4.8.1

## Details
### Impact
An attacker can send an invalid `Content-Type` header that can cause the application to crash, leading to a possible Denial of Service attack. Only the v4.x line is affected.

(This was updated: upon a close inspection, v3.x is not affected after all).

### Patches
Yes, update to `> v4.8.0`.

### Workarounds
You can reject the malicious content types before the body parser enters in action.
```js
  const badNames = Object.getOwnPropertyNames({}.__proto__)
  fastify.addHook('onRequest', async (req, reply) => {
    for (const badName of badNames) {
      if (req.headers['content-type'].indexOf(badName) > -1) {
        reply.code(415)
        throw new Error('Content type not supported')
      }
    }
  })
```

### References

See the HackerOne report [#1715536](https://hackerone.com/bugs?report_id=1715536&subject=fastify)

### For more information
[Fastify security policy](https://github.com/fastify/fastify/security/policy)

## References
- https://github.com/fastify/fastify/security/advisories/GHSA-455w-c45v-86rg
- https://nvd.nist.gov/vuln/detail/CVE-2022-39288
- https://github.com/fastify/fastify/commit/fbb07e8dfad74c69cd4cd2211aedab87194618e3
- https://github.com/fastify/fastify
- https://github.com/fastify/fastify/security/policy
- https://hackerone.com/bugs?report_id=1715536&subject=fastify
