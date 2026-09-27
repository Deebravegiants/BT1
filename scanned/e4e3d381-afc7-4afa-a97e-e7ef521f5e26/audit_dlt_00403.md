# [?] Count gasless tx for DoS protection (#25866)

## Summary
Severity: Unknown
Chain: Sui
Component: MystenLabs/sui
Published: 2026-03-30
Source: https://github.com/MystenLabs/sui/commit/54e640f65d70ba7f1fa280c458671b381d687ec7
Type: security-commit

## Details
Count gasless tx for DoS protection (#25866)

## Description 

Gasless tx should be counted in traffic controller since they have no
cost to sender.

## Test plan 

Added test

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
- [ ] Indexing Framework:

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
