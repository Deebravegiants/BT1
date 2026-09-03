# Q4782: LiFi swap: set feeToken == inputToken so inputAmoun [when the deposit uses proofles]

## Question
Can an unprivileged attacker in a LiFi swap action set feeToken == inputToken so inputAmount -= flatFee underflows or under-deducts, where the swap input diverges from the accounted delta, to either steal the output/fees or make Hinkal credit a UTXO larger than the value the action actually delivered, specifically when the deposit uses prooflessDeposit instead of a proof (where the no-proof mint path is taken)?

## Target
- File/function: contracts/external-actions/swaps/LifiExternalAction.sol :: callRouter / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact (LiFi action)
- Attacker controls: externalActionMetadata (router calldata), slippageValues, feeStructure, timeStamp, relay
- Exploit idea: decouple swappedAmount/fees from what the action forwards to Hinkal
- Invariant to test: amountToSendToHinkal == swappedAmount - totalFee and equals the credited UTXO
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry with a mock router: assert action residual or over-credit after swap
