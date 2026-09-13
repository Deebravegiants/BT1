# [H] @std/toml Prototype Pollution in Node.js and Browser

## Summary
Severity: High
Advisory: CVE-2025-55195
Aliases: GHSA-crjp-8r9q-2j9r
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-08-14
Source: https://osv.dev/vulnerability/CVE-2025-55195
Type: osv

## Details
@std/toml is the Deno Standard Library. Prior to version 1.0.9, an attacker can pollute the prototype chain in Node.js runtime and Browser when parsing untrusted TOML data, thus achieving Prototype Pollution (PP) vulnerability. This is because the library is merging an untrusted object with an empty object, which by default the empty object has the prototype chain. This issue has been patched in version 1.0.9.

## References
- https://github.com/denoland/std/releases/tag/release-2025.08.13
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/55xxx/CVE-2025-55195.json
- https://github.com/denoland/std/security/advisories/GHSA-crjp-8r9q-2j9r
- https://nvd.nist.gov/vuln/detail/CVE-2025-55195
- https://github.com/denoland/std/commit/540662cfd6d71e969af292aa604ef4049dbe271b
