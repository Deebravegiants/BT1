# Q0612: Preprocessing in Environment destroys the property being checked (python/occlusion.rs)

## Question
Can an unprivileged attacker exploit resizing/normalization/cropping in `Environment` in [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) that erases the exact texture or spectral cue a downstream anti-spoof check relies on, making a printed artifact indistinguishable from live tissue?

## Target
- File/function: [src/agents/python/occlusion.rs](src/agents/python/occlusion.rs) -> `Environment` (type)
- Entrypoint: Artifact whose distinguishing cue lies in the discarded band
- Attacker controls: the spatial/spectral characteristics of the presented artifact
- Exploit idea: Determine which cue the downstream check needs and whether `Environment` preserves it.
- Invariant to test: Preprocessing preserves every cue that downstream anti-spoof checks depend on.
- Expected Immunefi impact: Anti-spoof check defeated by preprocessing-induced information loss
- Fast validation: Differential test comparing check outcomes pre/post `Environment` on artifact vs. live samples.
