# Q3460: index startup policy race via #setFeatureFlags

## Question
Can an unprivileged attacker abuse wallet startup / refresh path that consumes default-enabled configuration state with crafted `config`, `name`, or stale-state timing so that `#setFeatureFlags` in `features/feature-flags/module/index.js` cause configuration to win a race against a safer local default at startup or resume, violating the invariant that safer local defaults must not be overwritten by stale or ambiguously merged remote state, and leading to `Direct theft of user funds`?

## Target
- File/function: features/feature-flags/module/index.js::#setFeatureFlags
- Entrypoint: wallet startup / refresh path that consumes default-enabled configuration state
- Attacker controls: feature-flag, fee-data, or remote URL fields that are consumed before account-sensitive checks
- Exploit idea: cause configuration to win a race against a safer local default at startup or resume
- Invariant to test: safer local defaults must not be overwritten by stale or ambiguously merged remote state
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: seed the persisted config atom with stale or conflicting values, restart the module, and assert safer defaults or fresh values win before sensitive actions occur
