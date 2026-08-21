# Q0651: Presentation attack accepted by EstimatePredictionLandmarksOutput (python/rgb_net.rs)

## Question
Can an unprivileged attacker present a high-resolution printed/screen-displayed iris or face (with IR-matched illumination) that `EstimatePredictionLandmarksOutput` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) accepts as a live subject because its accept criterion is a signal-quality/geometry threshold rather than a liveness proof?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `EstimatePredictionLandmarksOutput` (type)
- Entrypoint: Artifact held in front of the Orb during capture
- Attacker controls: print/display medium, IR reflectance, distance, and motion of the artifact
- Exploit idea: Identify exactly which measured properties `EstimatePredictionLandmarksOutput` requires and whether all are reproducible by a physical artifact.
- Invariant to test: Acceptance requires at least one property no static artifact can reproduce.
- Expected Immunefi impact: Enrollment/verification of a non-live subject, i.e. identity spoofing
- Fast validation: Replay test feeding artifact-derived frames through `EstimatePredictionLandmarksOutput` and asserting rejection.
