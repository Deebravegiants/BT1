# Q1752: Preprocessing in is_valid destroys the property being checked (face_identifier/mod.rs)

## Question
Can an unprivileged attacker exploit resizing/normalization/cropping in `is_valid` in [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) that erases the exact texture or spectral cue a downstream anti-spoof check relies on, making a printed artifact indistinguishable from live tissue?

## Target
- File/function: [src/agents/python/face_identifier/mod.rs](src/agents/python/face_identifier/mod.rs) -> `is_valid` (function)
- Entrypoint: Artifact whose distinguishing cue lies in the discarded band
- Attacker controls: the spatial/spectral characteristics of the presented artifact
- Exploit idea: Determine which cue the downstream check needs and whether `is_valid` preserves it.
- Invariant to test: Preprocessing preserves every cue that downstream anti-spoof checks depend on.
- Expected Immunefi impact: Anti-spoof check defeated by preprocessing-induced information loss
- Fast validation: Differential test comparing check outcomes pre/post `is_valid` on artifact vs. live samples.
