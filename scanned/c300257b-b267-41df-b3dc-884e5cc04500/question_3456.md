# Q3456: index stale config replay via FeatureFlags

## Question
Can an unprivileged attacker abuse wallet startup / refresh path that consumes default-enabled configuration state with crafted `port`, `config`, or stale-state timing so that `FeatureFlags` in `features/feature-flags/module/index.js` make cache validation skip a required refresh and preserve attacker-beneficial state, violating the invariant that config normalization must not widen privileges or weaken default security posture, and leading to `Direct theft of user funds`?

## Target
- File/function: features/feature-flags/module/index.js::FeatureFlags
- Entrypoint: wallet startup / refresh path that consumes default-enabled configuration state
- Attacker controls: persisted configuration state, cache validators, and normal startup / resume timing
- Exploit idea: make cache validation skip a required refresh and preserve attacker-beneficial state
- Invariant to test: config normalization must not widen privileges or weaken default security posture
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: seed the persisted config atom with stale or conflicting values, restart the module, and assert safer defaults or fresh values win before sensitive actions occur
