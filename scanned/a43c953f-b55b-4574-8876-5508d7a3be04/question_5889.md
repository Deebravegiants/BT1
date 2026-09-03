# Q5889: HinkalWallet control: exploit isValidSignature recovering addr [when the cited root is many ba]

## Question
Can an unprivileged attacker exploit isValidSignature recovering addr==address(this) via a crafted signature, where EIP-1271 verification compares the recovered address to the wallet itself, to drain the HinkalWallet's balance or make it approve/transfer to an attacker, specifically when the cited root is many batches old (where a stale historical root is used for inclusion)?

## Target
- File/function: contracts/external-actions/emporium/HinkalWallet.sol :: callHinkalWallet / doSendToRelay / isValidSignature
- Entrypoint: Hinkal.transact (Emporium op)
- Attacker controls: Emporium op endpoint/value/callData, relay argument, signature bytes
- Exploit idea: abuse the wallet's forwarding under Emporium identity
- Invariant to test: only ops the wallet owner signed move the wallet's assets
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry: fund a wallet, execute an op draining it, assert attacker gain
