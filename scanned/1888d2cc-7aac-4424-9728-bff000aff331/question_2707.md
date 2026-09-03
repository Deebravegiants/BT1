# Q2707: LiFi swap: point router calldata at a target that r [when a hook mutates state betw]

## Question
Can an unprivileged attacker in a LiFi swap action point router calldata at a target that returns output while approveUnlimited stays open, where a later caller spends the standing router allowance on the action's tokens, to either steal the output/fees or make Hinkal credit a UTXO larger than the value the action actually delivered, specifically when a hook mutates state between the check and the write (where the check-to-write gap is widened)?

## Target
- File/function: contracts/external-actions/swaps/LifiExternalAction.sol :: callRouter / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact (LiFi action)
- Attacker controls: externalActionMetadata (router calldata), slippageValues, feeStructure, timeStamp, relay
- Exploit idea: decouple swappedAmount/fees from what the action forwards to Hinkal
- Invariant to test: amountToSendToHinkal == swappedAmount - totalFee and equals the credited UTXO
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry with a mock router: assert action residual or over-credit after swap
