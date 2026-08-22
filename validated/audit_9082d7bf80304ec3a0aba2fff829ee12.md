### Title
Face self-custody RGB candidate selection uses session-wide highest score with no identity-continuity check, allowing a bystander's face frame to be bound to the enrolling user's iris capture - (File: src/plans/biometric_capture/mod.rs)

### Summary
`Plan::handle_face_identifier` selects the `self_custody_candidate_rgb` purely by comparing `output.score` against the maximum score seen across the *entire* biometric-capture session (both eye objectives), with no requirement that the winning RGB frame temporally or biometrically correspond to the same person whose iris frames (`left_ir`/`right_ir`) are being captured. A transient higher-scoring face in the camera's field of view during any objective can overwrite the previously stored candidate along with its paired `face_ir`/`thermal` frames, so the final self-custody package uploaded for the enrolling user's iris identity may contain a different person's face/IR/thermal data.

### Finding Description
In `handle_face_identifier` (src/plans/biometric_capture/mod.rs:289-323), each `IsValidImage` output is compared with:
```rust
let highest = self.self_custody_candidate_rgb.as_ref().map_or(0.0, |p| p.estimate.score.unwrap_or_default());
if output.score.is_some_and(|s| s > highest) {
    self.self_custody_candidate_rgb = Some(FrameInfoSelfCustodyCandidate::new(output, frame...));
    self.face_ir = self.last_face_ir.take();
    self.thermal = self.last_thermal.take();
}
```
This state (`self_custody_candidate_rgb`, `face_ir`, `thermal`) is initialized once in `Plan::new` (lines 406-421) and never reset between the left-eye and right-eye objectives, so `highest` is a running maximum spanning the whole signup, not a value scoped to a validated identity window. The only gate is `output.is_valid.map_or(false, |v| v)`, i.e. the frame is a plausible live face, not that it's the *same* face as the one whose iris is being scanned in `left_ir`/`right_ir` (populated independently in `handle_ir_net`, lines 217-268).

Because `rgb_net`/`face_identifier` process whatever face is currently visible to the RGB camera (see `handle_rgb_net`, lines 270-287, which only checks `bbox.coordinates.is_correct()` for the primary detected face), if a bystander's face transiently enters the RGB camera's frame with a higher `IsValidImage` score than the enrolling user's frame (e.g., due to lighting/angle/sharpness), that frame — and its paired `face_ir`/`thermal` captured via `last_face_ir`/`last_thermal` at that instant — becomes the final `face_self_custody_candidate` in `into_capture` (lines 557-600), regardless of which face's iris was ultimately captured for `left_ir`/`right_ir`. No code path cross-validates that the winning RGB face corresponds to the iris identity being enrolled.

### Impact Explanation
The resulting `Capture.face_self_custody_candidate` (rgb frame + IR/thermal) is encrypted and uploaded as the self-custody package bound to the attacker's iris code and `self_custody_user_public_key`. This causes disclosure/misappropriation of a bystander's biometric face/IR/thermal imagery into a signup record it does not belong to, and creates a wrong-identity binding between the enrolled iris and the stored face image — undermining any downstream use of the self-custody face data (e.g., later face-based recovery/verification or fraud analysis tied to that signup). This matches "biometric data disclosure" / "wrong-identity binding" bounty impact categories.

### Likelihood Explanation
Exploitability only requires an attacker (or an incidental bystander) to be transiently visible to the RGB camera at some point during their own signup session while scoring higher on the face-identifier's validity/quality metric than the enrolling user — a plausible occurrence given lighting/angle variance and no per-objective reset of the "highest score" tracking. No privileged access, key leakage, or MCU tampering is needed; it is purely a consequence of the unscoped global max-score comparison in `handle_face_identifier` and lack of a reset between objectives or identity-continuity check against `left_ir`/`right_ir`.

### Recommendation
Scope `self_custody_candidate_rgb` selection to a validated identity-continuity window: track the running max only within the current objective/eye-capture window, or re-validate the previously chosen candidate against a per-signup face-embedding/track ID derived from the iris capture windows before allowing a later frame to overwrite it. At minimum, reset `self_custody_candidate_rgb`/`face_ir`/`thermal` candidates whenever the RGB-net/IR-net indicates a change in tracked face/iris (e.g., discontinuity in bbox position, face ID from `rgb_net`, or gaps in `left_ir`/`right_ir` capture), and require the selected self-custody frame to be temporally correlated with a successfully captured, matching iris frame.

### Proof of Concept
Unit test in `src/plans/biometric_capture/mod.rs` test module:
1. Construct a `Plan` with two synthetic `IsValidImage` outputs/frames tagged "attacker" (score 0.5, valid) and "bystander" (score 0.9, valid) fed via `handle_face_identifier` during the left-eye objective, followed by valid `left_ir`/`left_rgb` frames tagged "attacker" fed via `handle_ir_net`/`handle_rgb_net`.
2. Continue into the right-eye objective, feeding another "attacker" `IsValidImage` (score 0.6, valid) and matching `right_ir`/`right_rgb` "attacker" frames.
3. Call `into_capture()` and assert that `face_self_custody_candidate.rgb_frame` corresponds to the "attacker" tag (matching `left_ir`/`right_ir`), not the "bystander" tag.
4. Current code will fail this assertion: `self_custody_candidate_rgb` will retain the bystander's frame (score 0.9) because `highest` is compared globally across both objectives with no identity-continuity check, demonstrating the wrong-identity binding.