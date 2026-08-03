# Q0465: control_inherited_account replay can reuse stale authorization

## Question
Can an unprivileged attacker replay `control_inherited_account` with stale approvals, announcements, timepoints, recovery attempts, or preimages and get a second execution after authorization should be spent or revoked?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::control_inherited_account
- Entrypoint: signed extrinsic `control_inherited_account`
- Attacker controls: nested call payloads
- Exploit idea: Exercise stale auth records with minimally changed parameters and ordering-sensitive retries.
- Invariant to test: A public authorization record must be single-use or exactly bounded in the way storage records it.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Create an authorization, consume it once, revoke or mutate it, then attempt every replay variant still accepted.
