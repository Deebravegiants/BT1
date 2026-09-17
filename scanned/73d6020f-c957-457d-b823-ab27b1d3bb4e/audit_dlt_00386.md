# [?] Bump crossbeam-epoch to 0.9.20 to fix RUSTSEC-2026-0204 (#27167)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-07-07
Source: https://github.com/MystenLabs/sui/commit/a17b4691909890b915fcdea8b2442da5f4b3bd6e
Type: security-commit

## Details
Bump crossbeam-epoch to 0.9.20 to fix RUSTSEC-2026-0204 (#27167)

## Description

The `cargo-deny (advisories)` CI job is failing on main due to
[RUSTSEC-2026-0204](https://rustsec.org/advisories/RUSTSEC-2026-0204)
(invalid pointer dereference in `fmt::Pointer` impl for
`Atomic`/`Shared` in crossbeam-epoch < 0.9.20). Bump the locked version
to 0.9.20 in the root, `external-crates/move`, and `examples/rust/*`
lockfiles.

## Test plan

`cargo deny check advisories` passes locally for both the root workspace
and `external-crates/move` with this change (it was the only outstanding
advisory).

## Release notes

Check each box that your changes affect. If none of the boxes relate to
your changes, release notes aren't required.

For each box you select, include information after the relevant heading
that describes the impact of your changes that a user might notice and
any actions they must take to implement updates.

- [ ] Protocol:
- [ ] Nodes (Validators and Full nodes):
- [ ] gRPC:
- [ ] JSON-RPC:
- [ ] GraphQL:
- [ ] CLI:
- [ ] Rust SDK:
