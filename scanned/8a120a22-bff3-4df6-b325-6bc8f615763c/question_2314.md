# Q2314: HinkalWallet control: route value through doSendToRelay to an  [when the same proof is reused ]

## Question
Can an unprivileged attacker route value through doSendToRelay to an attacker-controlled relay, where doSendToRelay trusts the Emporium caller's relay argument, to drain the HinkalWallet's balance or make it approve/transfer to an attacker, specifically when the same proof is reused with only calldata mutated (where the proof-to-calldata binding is stressed)?

## Target
- File/function: contracts/external-actions/emporium/HinkalWallet.sol :: callHinkalWallet / doSendToRelay / isValidSignature
- Entrypoint: Hinkal.transact (Emporium op)
- Attacker controls: Emporium op endpoint/value/callData, relay argument, signature bytes
- Exploit idea: abuse the wallet's forwarding under Emporium identity
- Invariant to test: only ops the wallet owner signed move the wallet's assets
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund a wallet, execute an op draining it, assert attacker gain
