# [H] ALPINE-CVE-2026-14380

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-14380
Ecosystem: Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-14380
Type: osv

## Affected
- Alpine:v3.24: `perl-dbi` — affected >=0 <1.651-r0

## Details
DBI versions before 1.650 for Perl are vulnerable to code injection via caller-influenced Profile.

When a string is assigned to a DBI handle's Profile attribute, DBI splits it into path, package and arguments, and interpolates the package part in a string eval with no validation of the package name.

Any caller-influenced value that reaches the Profile attribute is therefore arbitrary Perl code execution, including calls to run system commands.

The Profile attribute can be set from three different sources that can carry untrusted data: the DBI_PROFILE environment variable, a direct attribute assignment, and a DSN driver-attribute clause dbi:Driver(Profile=>SPEC):db.

An attacker controlling any of those inputs runs arbitrary Perl in the host process. The strongest remote position is a network-exposed DBI::Gofer / DBI::ProxyServer whose per-request DSN reaches the Profile attribute, letting a client execute code on the broker host.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-14380
