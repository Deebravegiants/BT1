# Q1960: request_blocks reuses cached validation state for non-equivalent blocks

## Question
Can an unprivileged attacker reach P2P message handler `request_blocks` and control non-equivalent blocks or proofs that collide in cache or dedup assumptions so that `CrawlerAPI.request_blocks` in `chia/seeder/crawler_api.py` executes a path where reuse cache, dedup, or seen-set assumptions in `request_blocks` for attacker-supplied objects that are not actually equivalent, violating the invariant that cache hits must never substitute for validating non-equivalent attacker-controlled data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/seeder/crawler_api.py:88 `CrawlerAPI.request_blocks`
- Entrypoint: P2P message handler `request_blocks`
- Attacker controls: non-equivalent blocks or proofs that collide in cache or dedup assumptions
- Exploit idea: reuse cache, dedup, or seen-set assumptions in `request_blocks` for attacker-supplied objects that are not actually equivalent
- Invariant to test: cache hits must never substitute for validating non-equivalent attacker-controlled data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: hit `chia/seeder/crawler_api.py:request_blocks` with non-equivalent objects that share cache-sensitive identifiers and assert no validation reuse changes outcome
