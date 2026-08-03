# Q0862: submit_commitment can duplicate relayer rewards or tips

## Question
Can an unprivileged attacker use `submit_commitment` to get the same relayer reward, tip, or payout credited twice from bridge-side accounting?

## Target
- File/function: bridges/modules/beefy/src/lib.rs::submit_commitment
- Entrypoint: public proof / message submission extrinsic `submit_commitment`
- Attacker controls: proof or signed payload contents
- Exploit idea: Target reward settlement paths that are keyed differently from proof acceptance paths.
- Invariant to test: Bridge proof acceptance and bridge reward settlement must be strictly one-to-one.
- Expected Immunefi impact: Forged cross-chain message or duplicated bridge payout / asset movement
- Fast validation: Observe reward-bearing flows, then replay acceptance, receipt, or tip settlement through every public variant that references the same object.
