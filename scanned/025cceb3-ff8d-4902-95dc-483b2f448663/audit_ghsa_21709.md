# [H] Uncaught Exception in fastify-multipart

## Summary
Severity: High
Advisory: GHSA-qh73-qc3p-rjv2
CVE: CVE-2021-23597
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-qh73-qc3p-rjv2
Type: github-advisory

## Affected
- npm: `fastify-multipart` — affected >=0 <5.3.1

## Details
### Impact

This is a bypass of CVE-2020-8136 (https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-8136).
By providing a `name=constructor` property it is still possible to crash the application.
The original fix only checks for the key `__proto__` (https://github.com/fastify/fastify-multipart/pull/116).

All users are recommended to upgrade

### Patches

v5.3.1 includes a patch
 
### Workarounds

No workarounds are possible.

### References

Read up https://www.fastify.io/docs/latest/Guides/Prototype-Poisoning/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/fastify/fastify-multipart](https://github.com/fastify/fastify-multipart)
* Email us at [hello@matteocollina.com](mailto:hello@matteocollina.com)

## References
- https://github.com/fastify/fastify-multipart/security/advisories/GHSA-qh73-qc3p-rjv2
- https://nvd.nist.gov/vuln/detail/CVE-2021-23597
- https://github.com/fastify/fastify-multipart/pull/116
- https://github.com/fastify/fastify-multipart/commit/a70dc7059a794589bd4fe066453141fc609e6066
- https://github.com/fastify/fastify-multipart
- https://github.com/fastify/fastify-multipart/releases/tag/v5.3.1
- https://snyk.io/vuln/SNYK-JS-FASTIFYMULTIPART-2395480
- https://www.fastify.io/docs/latest/Guides/Prototype-Poisoning
