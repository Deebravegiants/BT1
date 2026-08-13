# Q3315: feature flag atoms startup policy race via factory

## Question
Can an unprivileged attacker abuse wallet startup / refresh path that consumes default-enabled configuration state with crafted `config`, `name`, or stale-state timing so that `factory` in `features/feature-flags/atoms/feature-flag-atoms.js` cause configuration to win a race against a safer local default at startup or resume, violating the invariant that safer local defaults must not be overwritten by stale or ambiguously merged remote state, and leading to `Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction`?

## Target
- File/function: features/feature-flags/atoms/feature-flag-atoms.js::factory
- Entrypoint: wallet startup / refresh path that consumes default-enabled configuration state
- Attacker controls: feature-flag, fee-data, or remote URL fields that are consumed before account-sensitive checks
- Exploit idea: cause configuration to win a race against a safer local default at startup or resume
- Invariant to test: safer local defaults must not be overwritten by stale or ambiguously merged remote state
- Expected Immunefi impact: Changing sensitive details of other users (including modifying browser local storage) with up to one click of user interaction
- Fast validation: unit-test ETag / Last-Modified transitions and verify a required refresh is not skipped when effective policy changed
