# [M] age vulnerable to malicious plugin names, recipients, or identities causing arbitrary binary execution

## Summary
Severity: Medium
Advisory: GHSA-32gq-x56h-299c
CWE: CWE-25
Ecosystem: Go
Published: 2024-12-18
Source: https://github.com/advisories/GHSA-32gq-x56h-299c
Type: github-advisory

## Affected
- Go: `filippo.io/age` — affected >=0 <1.2.1

## Details
A plugin name containing a path separator may allow an attacker to execute an arbitrary binary.

Such a plugin name can be provided to the age CLI through an attacker-controlled recipient or identity string, or to the [`plugin.NewIdentity`](https://pkg.go.dev/filippo.io/age/plugin#NewIdentity), [`plugin.NewIdentityWithoutData`](https://pkg.go.dev/filippo.io/age/plugin#NewIdentityWithoutData), or [`plugin.NewRecipient`](https://pkg.go.dev/filippo.io/age/plugin#NewRecipient) APIs.

On UNIX systems, a directory matching `${TMPDIR:-/tmp}/age-plugin-*` needs to exist for the attack to succeed.

The binary is executed with a single flag, either `--age-plugin=recipient-v1` or `--age-plugin=identity-v1`. The standard input includes the recipient or identity string, and the random file key (if encrypting) or the header of the file (if decrypting). The format is constrained by the [age-plugin](https://c2sp.org/age-plugin) protocol.

An equivalent issue was fixed by the [rage](https://github.com/str4d/rage) project, see advisory [GHSA-4fg7-vxc8-qx5w](https://github.com/str4d/rage/security/advisories/GHSA-4fg7-vxc8-qx5w).

Thanks to ⬡-49016 for reporting this.

## References
- https://github.com/FiloSottile/age/security/advisories/GHSA-32gq-x56h-299c
- https://github.com/str4d/rage/security/advisories/GHSA-4fg7-vxc8-qx5w
- https://github.com/FiloSottile/age/commit/482cf6fc9babd3ab06f6606762aac10447222201
- https://github.com/FiloSottile/age
