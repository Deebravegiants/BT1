# Q2890: Preprocessing in init_sys_argv destroys the property being checked (python/mod.rs)

## Question
Can an unprivileged attacker exploit resizing/normalization/cropping in `init_sys_argv` in [src/agents/python/mod.rs](src/agents/python/mod.rs) that erases the exact texture or spectral cue a downstream anti-spoof check relies on, making a printed artifact indistinguishable from live tissue?

## Target
- File/function: [src/agents/python/mod.rs](src/agents/python/mod.rs) -> `init_sys_argv` (function)
- Entrypoint: Artifact whose distinguishing cue lies in the discarded band
- Attacker controls: the spatial/spectral characteristics of the presented artifact
- Exploit idea: Determine which cue the downstream check needs and whether `init_sys_argv` preserves it.
- Invariant to test: Preprocessing preserves every cue that downstream anti-spoof checks depend on.
- Expected Immunefi impact: Anti-spoof check defeated by preprocessing-induced information loss
- Fast validation: Differential test comparing check outcomes pre/post `init_sys_argv` on artifact vs. live samples.
