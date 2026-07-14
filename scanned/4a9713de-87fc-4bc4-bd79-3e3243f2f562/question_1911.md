# Q1911: new_unfinished_block trusts inconsistent proof or weight state

## Question
Can an unprivileged attacker reach P2P message handler `new_unfinished_block` and control block, header, proof, or weight fields supplied over the peer protocol so that `CrawlerAPI.new_unfinished_block` in `chia/seeder/crawler_api.py` executes a path where make `new_unfinished_block` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree, violating the invariant that honest nodes must derive the same chain weight and validity result from the same canonical data and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/seeder/crawler_api.py:60 `CrawlerAPI.new_unfinished_block`
- Entrypoint: P2P message handler `new_unfinished_block`
- Attacker controls: block, header, proof, or weight fields supplied over the peer protocol
- Exploit idea: make `new_unfinished_block` trust a malformed proof or chain-weight transition strongly enough that honest nodes can disagree
- Invariant to test: honest nodes must derive the same chain weight and validity result from the same canonical data
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: feed two peers the same malformed proof or weight sequence through `chia/seeder/crawler_api.py:new_unfinished_block` and assert both derive the same rejection
