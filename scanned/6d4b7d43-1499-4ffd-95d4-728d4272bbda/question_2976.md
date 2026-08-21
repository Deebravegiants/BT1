# Q2976: Index/bounds handling on model output in rgb_net_estimate (python/rgb_net.rs)

## Question
Can an unprivileged attacker cause `rgb_net_estimate` in [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) to index into a model output array whose length depends on detection count (faces, landmarks, regions), panicking or reading the wrong subject's entry when the count differs from the assumed one?

## Target
- File/function: [src/agents/python/rgb_net.rs](src/agents/python/rgb_net.rs) -> `rgb_net_estimate` (function)
- Entrypoint: Presenting multiple faces/subjects in frame
- Attacker controls: number and arrangement of subjects in the scene
- Exploit idea: Check `rgb_net_estimate` for hard-coded index 0 / assumed-length access over detection lists.
- Invariant to test: Detection lists are length-checked and the target subject is selected by an explicit identity rule.
- Expected Immunefi impact: Crash, or another bystander's biometrics selected as the signup subject
- Fast validation: Unit-test `rgb_net_estimate` with 0, 1, and N detections asserting correct subject selection and no panic.
