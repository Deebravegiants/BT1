# [C] ALPINE-CVE-2026-57075

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2026-57075
Ecosystem: Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-57075
Type: osv

## Affected
- Alpine:v3.24: `perl-yaml-syck` — affected >=0 <1.47-r0

## Details
YAML::Syck versions before 1.47 for Perl allow an out-of-bounds read via a signed-char lookup-table index in syck_base64dec.

The base64 decoder in the bundled libsyck indexes the 256-entry static table b64_xtable with a signed char, so any !!binary byte >= 0x80 sign-extends to a negative index and reads before the table. The decoder receives the raw bytes of any !!binary node, a standard YAML type not gated by $LoadBlessed or $LoadCode, so it is reached on the default Load path.

Any caller that runs Load or LoadFile on an untrusted document containing a !!binary scalar with a high-bit byte triggers the read, and the value read can surface in the decoded result.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-57075
