# Q1385: submit_delivery_receipt can update bridge state before decode or dispatch fails

## Question
Can an unprivileged attacker use `submit_delivery_receipt` so nonce, height, or imported-state markers advance before payload decode, message dispatch, or payout settlement later fails?

## Target
- File/function: bridges/snowbridge/pallets/outbound-queue-v2/src/lib.rs::submit_delivery_receipt
- Entrypoint: public proof / message submission extrinsic `submit_delivery_receipt`
- Attacker controls: proof or signed payload contents
- Exploit idea: Target late-failing paths after early monotonic state updates.
- Invariant to test: Bridge progress markers and payload effects must commit atomically or roll back together.
- Expected Immunefi impact: Bridge halt, chain halt, or invalid state root / header acceptance
- Fast validation: Craft proofs whose outer layer verifies but inner payload fails later and compare bridge markers before and after failure.
