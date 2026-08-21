# Q1601: Preprocessing in run_update_all_configs destroys the property being checked (biometric_pipeline/mod.rs)

## Question
Can an unprivileged attacker exploit resizing/normalization/cropping in `run_update_all_configs` in [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) that erases the exact texture or spectral cue a downstream anti-spoof check relies on, making a printed artifact indistinguishable from live tissue?

## Target
- File/function: [src/plans/biometric_pipeline/mod.rs](src/plans/biometric_pipeline/mod.rs) -> `run_update_all_configs` (function)
- Entrypoint: Artifact whose distinguishing cue lies in the discarded band
- Attacker controls: the spatial/spectral characteristics of the presented artifact
- Exploit idea: Determine which cue the downstream check needs and whether `run_update_all_configs` preserves it.
- Invariant to test: Preprocessing preserves every cue that downstream anti-spoof checks depend on.
- Expected Immunefi impact: Anti-spoof check defeated by preprocessing-induced information loss
- Fast validation: Differential test comparing check outcomes pre/post `run_update_all_configs` on artifact vs. live samples.
