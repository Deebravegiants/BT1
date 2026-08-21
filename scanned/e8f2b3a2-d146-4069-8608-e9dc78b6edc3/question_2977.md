# Q2977: Preprocessing in warmup destroys the property being checked (python/rgb_net.rs)

## Question
Can an unprivileged attacker exploit resizing/normalization/cropping in `warmup` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) that erases the exact texture or spectral cue a downstream anti-spoof check relies on, making a printed artifact indistinguishable from live tissue?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `warmup` (function)
- Entrypoint: Artifact whose distinguishing cue lies in the discarded band
- Attacker controls: the spatial/spectral characteristics of the presented artifact
- Exploit idea: Determine which cue the downstream check needs and whether `warmup` preserves it.
- Invariant to test: Preprocessing preserves every cue that downstream anti-spoof checks depend on.
- Expected Immunefi impact: Anti-spoof check defeated by preprocessing-induced information loss
- Fast validation: Differential test comparing check outcomes pre/post `warmup` on artifact vs. live samples.
