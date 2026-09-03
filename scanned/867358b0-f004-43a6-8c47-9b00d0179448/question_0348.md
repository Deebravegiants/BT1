# Q0348: LiFi swap: supply timeStamp so block.timestamp <= t [across a batch of transactions]

## Question
Can an unprivileged attacker in a LiFi swap action supply timeStamp so block.timestamp <= timeStamp + SWAP_DEADLINE_WINDOW using a future stamp, where the deadline check is satisfied by an attacker-chosen future timeStamp, to either steal the output/fees or make Hinkal credit a UTXO larger than the value the action actually delivered, specifically across a batch of transactions landing in one block (where batching and ordering change the observable pre/post state)?

## Target
- File/function: contracts/external-actions/swaps/LifiExternalAction.sol :: callRouter / ExternalActionSwap.swap
- Entrypoint: Hinkal.transact (LiFi action)
- Attacker controls: externalActionMetadata (router calldata), slippageValues, feeStructure, timeStamp, relay
- Exploit idea: decouple swappedAmount/fees from what the action forwards to Hinkal
- Invariant to test: amountToSendToHinkal == swappedAmount - totalFee and equals the credited UTXO
- Expected Immunefi impact: Critical: direct theft of shielded or in-flight user funds
- Fast validation: Foundry with a mock router: assert action residual or over-credit after swap
