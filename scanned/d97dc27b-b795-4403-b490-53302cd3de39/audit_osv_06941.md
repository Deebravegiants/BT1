# [M] Arbitrary command execution via shell-expanded connection string in Launch MongoDB Shell terminal

## Summary
Severity: Medium
Advisory: BIT-mongodb-2026-84967
Aliases: CVE-2026-84967
Ecosystem: Bitnami
Published: 2026-09-10
Source: https://osv.dev/vulnerability/BIT-mongodb-2026-84967
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=1.13.0 <1.17.1

## Details
A component of the MongoDB extension for Visual Studio Code does not neutralize special characters in a connection string before that value is placed into a command line the extension composes for an integrated terminal. An unauthenticated remote unauthorized-user who persuades a developer to accept a user-supplied connection target, and then to open the extension's shell feature, can place characters of the unauthorized-user’s choosing into that command line. No privileges on the developer's machine are required, but several user actions are. The confirmation the developer sees does not display the supplied text.

## References
- https://jira.mongodb.org/browse/VSCODE-798
- https://nvd.nist.gov/vuln/detail/CVE-2026-84967
