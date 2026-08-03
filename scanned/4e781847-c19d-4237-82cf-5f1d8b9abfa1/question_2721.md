# Q2721: redeem can write state that another public path misreads

## Question
Can an unprivileged attacker use `redeem` to create or mutate storage that a different public entrypoint later interprets more permissively than intended?

## Target
- File/function: substrate/frame/psm/src/lib.rs::redeem
- Entrypoint: signed extrinsic `redeem`
- Attacker controls: amounts, fees, or prices
- Exploit idea: Look for state shared across multiple public entrypoints but validated differently by each one.
- Invariant to test: Shared storage must have one consistent meaning across every public path that consumes it.
- Expected Immunefi impact: Theft of user funds / unbacked mint or pool insolvency
- Fast validation: After exercising the entrypoint, call every other public function that touches the same object family and check for inconsistent interpretation.
