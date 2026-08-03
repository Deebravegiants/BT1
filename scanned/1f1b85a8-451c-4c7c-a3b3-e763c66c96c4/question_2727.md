# Q2727: payout_stakers_by_page can write state that another public path misreads

## Question
Can an unprivileged attacker use `payout_stakers_by_page` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/staking/src/pallet/mod.rs::payout_stakers_by_page
- Entrypoint: signed extrinsic `payout_stakers_by_page`
- Attacker controls: call repetition, batching order, and surrounding state
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.
