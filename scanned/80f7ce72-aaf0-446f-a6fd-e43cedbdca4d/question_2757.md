# Q2757: LiFi swap: set feeToken == inputToken so inputAmoun [when a hook mutates state betw]

## Question
Can an unprivileged attacker in a LiFi swap action set feeToken == inputToken so inputAmount -= flatFee underflows or under-deducts, where the swap input diverges from the accounted delta, to either steal the output/fees or make Hinkal credit a UTXO larger than the value the action actually delivered, specifically when a hook mutates state between the check and the write (where the check-to-write gap is widened)?

## Target
- File/function: contracts/external-actions/swaps/LifiExternalAction.sol :: callRouter / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact (LiFi action)
- Attacker controls: externalActionMetadata (router calldata), slippageValues, feeStructure, timeStamp, relay
- Exploit idea: decouple swappedAmount/fees from what the action forwards to Hinkal
- Invariant to test: amountToSendToHinkal == swappedAmount - totalFee and equals the credited UTXO
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry with a mock router: assert action residual or over-credit after swap
