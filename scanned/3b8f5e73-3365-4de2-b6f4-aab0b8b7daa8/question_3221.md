# Q3221: index stale config replay via update

## Question
Can an unprivileged attacker abuse wallet startup or resume path that loads persisted or fetched remote configuration with crafted `remoteConfigUrl`, `lastModified`, or stale-state timing so that `update` in `features/remote-config/module/index.ts` make cache validation skip a required refresh and preserve attacker-beneficial state, violating the invariant that config normalization must not widen privileges or weaken default security posture, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/remote-config/module/index.ts::update
- Entrypoint: wallet startup or resume path that loads persisted or fetched remote configuration
- Attacker controls: persisted configuration state, cache validators, and normal startup / resume timing
- Exploit idea: make cache validation skip a required refresh and preserve attacker-beneficial state
- Invariant to test: config normalization must not widen privileges or weaken default security posture
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: unit-test ETag / Last-Modified transitions and verify a required refresh is not skipped when effective policy changed
