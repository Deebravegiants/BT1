# Q3190: index startup policy race via createRemoteConfig

## Question
Can an unprivileged attacker abuse wallet startup or resume path that loads persisted or fetched remote configuration with crafted `lastModified`, `config`, or stale-state timing so that `createRemoteConfig` in `features/remote-config/module/index.ts` cause configuration to win a race against a safer local default at startup or resume, violating the invariant that safer local defaults must not be overwritten by stale or ambiguously merged remote state, and leading to `Direct theft of user funds`?

## Target
- File/function: features/remote-config/module/index.ts::createRemoteConfig
- Entrypoint: wallet startup or resume path that loads persisted or fetched remote configuration
- Attacker controls: feature-flag, fee-data, or remote URL fields that are consumed before account-sensitive checks
- Exploit idea: cause configuration to win a race against a safer local default at startup or resume
- Invariant to test: safer local defaults must not be overwritten by stale or ambiguously merged remote state
- Expected Immunefi impact: Direct theft of user funds
- Fast validation: seed the persisted config atom with stale or conflicting values, restart the module, and assert safer defaults or fresh values win before sensitive actions occur
