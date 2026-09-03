# Q1882: LiFi swap: relay == address(0) so sendToRelay no-op [at the maximum allowed array l]

## Question
Can an unprivileged attacker in a LiFi swap action relay == address(0) so sendToRelay no-ops and hinkalFee/relayFee stay in the action, where fees intended for the relay are stranded and later reclaimable, to either steal the output/fees or make Hinkal credit a UTXO larger than the value the action actually delivered, specifically at the maximum allowed array lengths (where boundary sizing exposes off-by-one behaviour)?

## Target
- File/function: contracts/external-actions/swaps/LifiExternalAction.sol :: callRouter / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact (LiFi action)
- Attacker controls: externalActionMetadata (router calldata), slippageValues, feeStructure, timeStamp, relay
- Exploit idea: decouple swappedAmount/fees from what the action forwards to Hinkal
- Invariant to test: amountToSendToHinkal == swappedAmount - totalFee and equals the credited UTXO
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry with a mock router: assert action residual or over-credit after swap
