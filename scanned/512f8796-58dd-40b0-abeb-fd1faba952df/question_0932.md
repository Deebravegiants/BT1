# Q0932: LiFi swap: choose slippageValues[1] just above zero [under a token with 6 decimals]

## Question
Can an unprivileged attacker in a LiFi swap action choose slippageValues[1] just above zero so the balance require passes on a near-empty swap, where swappedAmount is minimal yet balanceDif clears the slippage floor, to either steal the output/fees or make Hinkal credit a UTXO larger than the value the action actually delivered, specifically under a token with 6 decimals (where decimal scaling shifts the accounting boundary)?

## Target
- File/function: contracts/external-actions/swaps/LifiExternalAction.sol :: callRouter / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact (LiFi action)
- Attacker controls: externalActionMetadata (router calldata), slippageValues, feeStructure, timeStamp, relay
- Exploit idea: decouple swappedAmount/fees from what the action forwards to Hinkal
- Invariant to test: amountToSendToHinkal == swappedAmount - totalFee and equals the credited UTXO
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry with a mock router: assert action residual or over-credit after swap
