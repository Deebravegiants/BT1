# Q0469: set_friend_groups replay can reuse stale authorization

## Question
Can an unprivileged attacker replay `set_friend_groups` with stale approvals, announcements, timepoints, recovery attempts, or preimages and get a second execution after authorization should be spent or revoked?

## Target
- File/function: substrate/frame/recovery/src/lib.rs::set_friend_groups
- Entrypoint: signed extrinsic `set_friend_groups`
- Attacker controls: duplicate or adversarial list ordering
- Exploit idea: Exercise stale auth records with minimally changed parameters and ordering-sensitive retries.
- Invariant to test: A public authorization record must be single-use or exactly bounded in the way storage records it.
- Expected Immunefi impact: Unauthorized account or call control leading to fund theft or governance capture
- Fast validation: Create an authorization, consume it once, revoke or mutate it, then attempt every replay variant still accepted.
