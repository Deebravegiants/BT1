# Q0462: remove_proxy replay can reuse stale authorization

## Question
Can an unprivileged attacker replay `remove_proxy` with stale approvals, announcements, timepoints, recovery attempts, or preimages and get a second execution after authorization should be spent or revoked?

## Target
- File/function: substrate/frame/proxy/src/lib.rs::remove_proxy
- Entrypoint: public dispatch wrapper `remove_proxy`
- Attacker controls: nested call payloads, beneficiary, delegate, or target accounts, batched or wrapped execution context
- Exploit idea: Exercise stale auth records with minimally changed parameters and ordering-sensitive retries.
- Invariant to test: A public authorization record must be single-use or exactly bounded in the way storage records it.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Create an authorization, consume it once, revoke or mutate it, then attempt every replay variant still accepted.
