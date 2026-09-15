# [M] Remote DoS from malformed RESTORE command

## Summary
Severity: Medium
Advisory: CVE-2026-21864
Aliases: GHSA-mc2g-h759-3qw2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-21864
Type: osv

## Details
Valkey-Bloom is a Rust based Valkey module which brings a Bloom Filter (Module) data type into the Valkey distributed key-value database. Prior to commit a68614b6e3845777d383b3a513cedcc08b3b7ccd, a specially crafted `RESTORE` command can cause Valkey to hit an assertion, causes the server to shutdown. Valkey modules are required to handle errors in RDB parsing by using `VALKEYMODULE_OPTIONS_HANDLE_IO_ERRORS` flag. If this flag is not set, errors encountered during parsing result in a system assertion which shuts down the system. Even though the Valkey-bloom module correctly handled the parsing, it did not originally set the flag. Commit a68614b6e3845777d383b3a513cedcc08b3b7ccd contains a patch. One may mitigate this defect by disabling the `RESTORE` command if it is unused by one's application.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21864.json
- https://github.com/valkey-io/valkey-bloom/security/advisories/GHSA-mc2g-h759-3qw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-21864
- https://github.com/valkey-io/valkey-bloom/commit/a68614b6e3845777d383b3a513cedcc08b3b7ccd
