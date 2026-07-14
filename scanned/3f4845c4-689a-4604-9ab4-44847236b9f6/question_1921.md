# Q1921: new_unfinished_block2 evaluates attacker-controlled generators differently across nodes

## Question
Can an unprivileged attacker reach P2P message handler `new_unfinished_block2` and control generator refs, decompressed program bytes, and block-to-generator linkage so that `CrawlerAPI.new_unfinished_block2` in `chia/seeder/crawler_api.py` executes a path where cause `new_unfinished_block2` to execute or reference generator data differently from the canonical block context, violating the invariant that all honest nodes must execute the same generator bytes and references for the same block context and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/seeder/crawler_api.py:64 `CrawlerAPI.new_unfinished_block2`
- Entrypoint: P2P message handler `new_unfinished_block2`
- Attacker controls: generator refs, decompressed program bytes, and block-to-generator linkage
- Exploit idea: cause `new_unfinished_block2` to execute or reference generator data differently from the canonical block context
- Invariant to test: all honest nodes must execute the same generator bytes and references for the same block context
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: build paired blocks with generator-ref edge cases and assert `chia/seeder/crawler_api.py:new_unfinished_block2` executes identical generator bytes on every path
