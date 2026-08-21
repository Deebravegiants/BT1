# Q1763: Preprocessing in Bundle destroys the property being checked (face_identifier/types.rs)

## Question
Can an unprivileged attacker exploit resizing/normalization/cropping in `Bundle` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) that erases the exact texture or spectral cue a downstream anti-spoof check relies on, making a printed artifact indistinguishable from live tissue?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `Bundle` (type)
- Entrypoint: Artifact whose distinguishing cue lies in the discarded band
- Attacker controls: the spatial/spectral characteristics of the presented artifact
- Exploit idea: Determine which cue the downstream check needs and whether `Bundle` preserves it.
- Invariant to test: Preprocessing preserves every cue that downstream anti-spoof checks depend on.
- Expected Immunefi impact: Anti-spoof check defeated by preprocessing-induced information loss
- Fast validation: Differential test comparing check outcomes pre/post `Bundle` on artifact vs. live samples.
