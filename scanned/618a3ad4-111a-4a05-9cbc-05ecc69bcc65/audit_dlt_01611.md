# [?] [traffic controller] fix race condition in blocklist metric dec() call (#22771)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2025-07-17
Source: https://github.com/MystenLabs/sui/commit/6427b4d62842d9f4487521a0f69163233dc06be2
Type: security-commit

## Details
[traffic controller] fix race condition in blocklist metric dec() call (#22771)

## Description 

the blocklist len metric often reports as being a negative number, which
shouldn't be possible. This fixes a possible race condition where the
same IP is triggering `check_and_clear_blocklist` in parallel, causing
the blocklist to be decremented multiple times when only a single IP is
being removed.

## Test plan 

How did you test the new or updated feature?

---

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
