# Q1502: Index/bounds handling on model output in failure_feedback (biometric_capture/mod.rs)

## Question
Can an unprivileged attacker cause `failure_feedback` in [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) to index into a model output array whose length depends on detection count (faces, landmarks, regions), panicking or reading the wrong subject's entry when the count differs from the assumed one?

## Target
- File/function: [src/plans/biometric_capture/mod.rs](src/plans/biometric_capture/mod.rs) -> `failure_feedback` (function)
- Entrypoint: Presenting multiple faces/subjects in frame
- Attacker controls: number and arrangement of subjects in the scene
- Exploit idea: Check `failure_feedback` for hard-coded index 0 / assumed-length access over detection lists.
- Invariant to test: Detection lists are length-checked and the target subject is selected by an explicit identity rule.
- Expected Immunefi impact: Crash, or another bystander's biometrics selected as the signup subject
- Fast validation: Unit-test `failure_feedback` with 0, 1, and N detections asserting correct subject selection and no panic.
