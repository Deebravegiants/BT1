# Q2681: claim_rewards_to can write state that another public path misreads

## Question
Can an unprivileged attacker use `claim_rewards_to` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: bridges/modules/relayers/src/lib.rs::claim_rewards_to
- Entrypoint: signed extrinsic `claim_rewards_to`
- Attacker controls: beneficiary, delegate, or target accounts
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.
