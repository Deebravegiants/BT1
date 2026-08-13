# Q3291: feature flag atoms stale config replay via factory

## Question
Can an unprivileged attacker abuse wallet startup / refresh path that consumes default-enabled configuration state with crafted `config`, `name`, or stale-state timing so that `factory` in `features/feature-flags/atoms/feature-flag-atoms.js` make cache validation skip a required refresh and preserve attacker-beneficial state, violating the invariant that config normalization must not widen privileges or weaken default security posture, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/feature-flags/atoms/feature-flag-atoms.js::factory
- Entrypoint: wallet startup / refresh path that consumes default-enabled configuration state
- Attacker controls: persisted configuration state, cache validators, and normal startup / resume timing
- Exploit idea: make cache validation skip a required refresh and preserve attacker-beneficial state
- Invariant to test: config normalization must not widen privileges or weaken default security posture
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: unit-test ETag / Last-Modified transitions and verify a required refresh is not skipped when effective policy changed
