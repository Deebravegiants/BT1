# [C] YAML::Syck versions before 1.47 for Perl allow an out-of-bounds read via a signed-char lookup-table index in syck_base64dec

## Summary
Severity: Critical
Advisory: CVE-2026-57075
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-57075
Type: osv

## Details
YAML::Syck versions before 1.47 for Perl allow an out-of-bounds read via a signed-char lookup-table index in syck_base64dec.

The base64 decoder in the bundled libsyck indexes the 256-entry static table b64_xtable with a signed char, so any !!binary byte >= 0x80 sign-extends to a negative index and reads before the table. The decoder receives the raw bytes of any !!binary node, a standard YAML type not gated by $LoadBlessed or $LoadCode, so it is reached on the default Load path.

Any caller that runs Load or LoadFile on an untrusted document containing a !!binary scalar with a high-bit byte triggers the read, and the value read can surface in the decoded result.

## References
- http://www.openwall.com/lists/oss-security/2026/07/17/2
- https://cpan.org/modules
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57075.json
- https://metacpan.org/release/TODDR/YAML-Syck-1.47/changes
- https://nvd.nist.gov/vuln/detail/CVE-2026-57075
- https://github.com/toddr/YAML-Syck/commit/44c90a109ec3215ee7ce747bd11209835e123d8b.patch
- https://github.com/toddr/YAML-Syck
