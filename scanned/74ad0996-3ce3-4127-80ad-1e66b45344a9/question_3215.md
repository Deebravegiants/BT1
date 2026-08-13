# Q3215: index startup policy race via RemoteConfig

## Question
Can an unprivileged attacker abuse wallet startup or resume path that loads persisted or fetched remote configuration with crafted `config`, `name`, or stale-state timing so that `RemoteConfig` in `features/remote-config/module/index.ts` cause configuration to win a race against a safer local default at startup or resume, violating the invariant that safer local defaults must not be overwritten by stale or ambiguously merged remote state, and leading to `Taking state-modifying authenticated actions on behalf of other users without any interaction by that user`?

## Target
- File/function: features/remote-config/module/index.ts::RemoteConfig
- Entrypoint: wallet startup or resume path that loads persisted or fetched remote configuration
- Attacker controls: feature-flag, fee-data, or remote URL fields that are consumed before account-sensitive checks
- Exploit idea: cause configuration to win a race against a safer local default at startup or resume
- Invariant to test: safer local defaults must not be overwritten by stale or ambiguously merged remote state
- Expected Immunefi impact: Taking state-modifying authenticated actions on behalf of other users without any interaction by that user
- Fast validation: load config for one network or account context, switch context, and ensure fee or policy data is not silently reused
