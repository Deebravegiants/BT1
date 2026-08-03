# Q0444: unbind_username replay can reuse stale authorization

## Question
Can an unprivileged attacker replay `unbind_username` with stale approvals, announcements, timepoints, recovery attempts, or preimages and get a second execution after authorization should be spent or revoked?

## Target
- File/function: substrate/frame/identity/src/lib.rs::unbind_username
- Entrypoint: signed extrinsic `unbind_username`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Exercise stale auth records with minimally changed parameters and ordering-sensitive retries.
- Invariant to test: A public authorization record must be single-use or exactly bounded in the way storage records it.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Create an authorization, consume it once, revoke or mutate it, then attempt every replay variant still accepted.
