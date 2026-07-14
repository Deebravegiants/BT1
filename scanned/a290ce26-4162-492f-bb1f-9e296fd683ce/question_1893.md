# Q1893: new_peak derives fork choice from attacker-malleable intermediate state

## Question
Can an unprivileged attacker reach P2P message handler `new_peak` and control fork-choice inputs, intermediate peak state, and peer delivery order so that `CrawlerAPI.new_peak` in `chia/seeder/crawler_api.py` executes a path where make `new_peak` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state, violating the invariant that fork choice must depend only on canonical validated chain state, not attacker-shaped transient state and leading to Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction?

## Target
- File/function: chia/seeder/crawler_api.py:45 `CrawlerAPI.new_peak`
- Entrypoint: P2P message handler `new_peak`
- Attacker controls: fork-choice inputs, intermediate peak state, and peer delivery order
- Exploit idea: make `new_peak` commit fork-choice decisions from attacker-malleable intermediate state instead of canonical chain state
- Invariant to test: fork choice must depend only on canonical validated chain state, not attacker-shaped transient state
- Expected Immunefi impact: Consensus divergence, deterministic validation mismatch, invalid block or spend acceptance, forged weight proof trust, or chain halt caused by an unprivileged block, spend bundle, protocol message, sync path, or mempool interaction
- Fast validation: deliver competing peaks and blocks around `chia/seeder/crawler_api.py:new_peak` and assert fork choice depends only on canonical validated state
