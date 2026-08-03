# Q0454: announce replay can reuse stale authorization

## Question
Can an unprivileged attacker replay `announce` with stale approvals, announcements, timepoints, recovery attempts, or preimages and get a second execution after authorization should be spent or revoked?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::announce
- Entrypoint: public dispatch wrapper `announce`
- Attacker controls: batched or wrapped execution context
- Exploit idea: Exercise stale auth records with minimally changed parameters and ordering-sensitive retries.
- Invariant to test: A public authorization record must be single-use or exactly bounded in the way storage records it.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Create an authorization, consume it once, revoke or mutate it, then attempt every replay variant still accepted.
