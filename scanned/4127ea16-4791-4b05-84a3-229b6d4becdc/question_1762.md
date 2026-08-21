# Q1762: Index/bounds handling on model output in extract_option_rkyv_ndarray_d3 (face_identifier/types.rs)

## Question
Can an unprivileged attacker cause `extract_option_rkyv_ndarray_d3` in [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) to index into a model output array whose length depends on detection count (faces, landmarks, regions), panicking or reading the wrong subject's entry when the count differs from the assumed one?

## Target
- File/function: [src/agents/python/face_identifier/types.rs](src/agents/python/face_identifier/types.rs) -> `extract_option_rkyv_ndarray_d3` (function)
- Entrypoint: Presenting multiple faces/subjects in frame
- Attacker controls: number and arrangement of subjects in the scene
- Exploit idea: Check `extract_option_rkyv_ndarray_d3` for hard-coded index 0 / assumed-length access over detection lists.
- Invariant to test: Detection lists are length-checked and the target subject is selected by an explicit identity rule.
- Expected Immunefi impact: Crash, or another bystander's biometrics selected as the signup subject
- Fast validation: Unit-test `extract_option_rkyv_ndarray_d3` with 0, 1, and N detections asserting correct subject selection and no panic.
