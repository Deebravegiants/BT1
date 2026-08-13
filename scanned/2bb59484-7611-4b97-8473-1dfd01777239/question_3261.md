# Q3261: feature flag atoms stale config replay via factory

## Question
Can an unprivileged attacker abuse wallet startup / refresh path that consumes default-enabled configuration state with crafted `config`, `name`, or stale-state timing so that `factory` in `features/feature-flags/atoms/feature-flag-atoms.js` make cache validation skip a required refresh and preserve attacker-beneficial state, violating the invariant that config normalization must not widen privileges or weaken default security posture, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/feature-flags/atoms/feature-flag-atoms.js::factory
- Entrypoint: wallet startup / refresh path that consumes default-enabled configuration state
- Attacker controls: persisted configuration state, cache validators, and normal startup / resume timing
- Exploit idea: make cache validation skip a required refresh and preserve attacker-beneficial state
- Invariant to test: config normalization must not widen privileges or weaken default security posture
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: load config for one network or account context, switch context, and ensure fee or policy data is not silently reused
