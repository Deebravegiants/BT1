# Q1991: request_block_header mixes fork state across rollback or peak changes

## Question
Can an unprivileged attacker reach P2P message handler `request_block_header` and control peak announcements, fork shapes, rollback order, and block delivery timing so that `CrawlerAPI.request_block_header` in `chia/seeder/crawler_api.py` executes a path where interleave peak changes and rollback-sensitive inputs so `request_block_header` mixes fork-specific state across chains, violating the invariant that fork-local state must not leak across rollback and reorg boundaries and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/seeder/crawler_api.py:112 `CrawlerAPI.request_block_header`
- Entrypoint: P2P message handler `request_block_header`
- Attacker controls: peak announcements, fork shapes, rollback order, and block delivery timing
- Exploit idea: interleave peak changes and rollback-sensitive inputs so `request_block_header` mixes fork-specific state across chains
- Invariant to test: fork-local state must not leak across rollback and reorg boundaries
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: script a reorg harness around `chia/seeder/crawler_api.py:request_block_header` with interleaved peaks and assert fork-local state never leaks across rollback
