# Q5664: HinkalWallet control: exploit isValidSignature recovering addr [when the tree has exactly one ]

## Question
Can an unprivileged attacker exploit isValidSignature recovering addr==address(this) via a crafted signature, where EIP-1271 verification compares the recovered address to the wallet itself, to drain the HinkalWallet's balance or make it approve/transfer to an attacker, specifically when the tree has exactly one prior leaf (where roots[MINIMUM_INDEX] equals that leaf directly)?

## Target
- File/function: contracts/external-actions/emporium/HinkalWallet.sol :: callHinkalWallet / doSendToRelay / isValidSignature
- Entrypoint: Hinkal.transact (Emporium op)
- Attacker controls: Emporium op endpoint/value/callData, relay argument, signature bytes
- Exploit idea: abuse the wallet's forwarding under Emporium identity
- Invariant to test: only ops the wallet owner signed move the wallet's assets
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund a wallet, execute an op draining it, assert attacker gain
