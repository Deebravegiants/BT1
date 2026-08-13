# Q3346: remote config feature flags stale config replay via factory

## Question
Can an unprivileged attacker abuse wallet startup or resume path that loads persisted or fetched remote configuration with crafted `port`, `config`, or stale-state timing so that `factory` in `features/feature-flags/atoms/remote-config-feature-flags.js` make cache validation skip a required refresh and preserve attacker-beneficial state, violating the invariant that config normalization must not widen privileges or weaken default security posture, and leading to `Sitewide disruption of core services`?

## Target
- File/function: features/feature-flags/atoms/remote-config-feature-flags.js::factory
- Entrypoint: wallet startup or resume path that loads persisted or fetched remote configuration
- Attacker controls: persisted configuration state, cache validators, and normal startup / resume timing
- Exploit idea: make cache validation skip a required refresh and preserve attacker-beneficial state
- Invariant to test: config normalization must not widen privileges or weaken default security posture
- Expected Immunefi impact: Sitewide disruption of core services
- Fast validation: fuzz config normalization with ambiguous booleans, arrays, and object merges and assert no privilege-widening output is produced
