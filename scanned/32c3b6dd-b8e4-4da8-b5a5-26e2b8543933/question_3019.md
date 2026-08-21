# Q3019: Preprocessing in from_py_err destroys the property being checked (ai-interface/lib.rs)

## Question
Can an unprivileged attacker exploit resizing/normalization/cropping in `from_py_err` in [ai-interface/src/lib.rs](ai-interface/src/lib.rs) that erases the exact texture or spectral cue a downstream anti-spoof check relies on, making a printed artifact indistinguishable from live tissue?

## Target
- File/function: [ai-interface/src/lib.rs](ai-interface/src/lib.rs) -> `from_py_err` (function)
- Entrypoint: Artifact whose distinguishing cue lies in the discarded band
- Attacker controls: the spatial/spectral characteristics of the presented artifact
- Exploit idea: Determine which cue the downstream check needs and whether `from_py_err` preserves it.
- Invariant to test: Preprocessing preserves every cue that downstream anti-spoof checks depend on.
- Expected Immunefi impact: Anti-spoof check defeated by preprocessing-induced information loss
- Fast validation: Differential test comparing check outcomes pre/post `from_py_err` on artifact vs. live samples.
