# [H] Uncaught Exception in mercurius

## Summary
Severity: High
Advisory: GHSA-273r-rm8g-7f3x
CVE: CVE-2021-43801
CWE: CWE-754
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-12-13
Source: https://github.com/advisories/GHSA-273r-rm8g-7f3x
Type: github-advisory

## Affected
- npm: `mercurius` — affected >=8.10.0 <8.11.2

## Details
### Impact

Any users from Mercurius@8.10.0 to 8.11.1 are subjected to a denial of service attack by sending a malformed JSON to `/graphql` unless they are using a custom error handler.

### Patches

The vulnerability has been fixed in https://github.com/mercurius-js/mercurius/pull/678 and shipped as v8.11.2.

### Workarounds

Use a custom error handler.

### References

See https://github.com/mercurius-js/mercurius/issues/677

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/mercurius-js/mercurius
* Email us at [hello@matteocollina.com](mailto:hello@matteocollina.com)

## References
- https://github.com/mercurius-js/mercurius/security/advisories/GHSA-273r-rm8g-7f3x
- https://nvd.nist.gov/vuln/detail/CVE-2021-43801
- https://github.com/mercurius-js/mercurius/issues/677
- https://github.com/mercurius-js/mercurius/pull/678/commits/732b2f895312da8deadd7b173dcd2d141d54b223
- https://github.com/mercurius-js/mercurius
