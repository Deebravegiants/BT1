# [?] fix(blocksync): removeTimedoutPeers deadlock found via Byzantine prevote gossip race (#5839)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cometbft/cometbft
Published: 2026-05-11
Source: https://github.com/cometbft/cometbft/commit/55ea8536d004161ad95b91b4ffc41ddfbfc9e0cb
Type: security-commit

## Details
fix(blocksync): removeTimedoutPeers deadlock found via Byzantine prevote gossip race (#5839)

---
Fix the CI failure at:

https://github.com/cometbft/cometbft/actions/runs/25498058929/job/74823025038

That run revealed two issues:

1. removeTimedoutPeers and onTimeout held pool.mtx while calling
   sendError, which blocks on errorsCh. The reactor loop (the only
   consumer) may itself wait for pool.mtx via AddBlock, forming a
   circular deadlock.

2. The split-delivery of conflicting prevotes required gossip to
   propagate before height 2 committed, which raced under -race.
   Fix: send both conflicting prevotes to every peer directly so each
   validator detects the equivocation without relying on gossip timing.

Follows up on #5814
#### PR checklist

- [x] Tests written/updated
- [ ] Changelog entry added in `CHANGELOG.md`
- [ ] Updated relevant documentation (`docs/` or `spec/`) and code
comments
