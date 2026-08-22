# [M] Kleros will not be able to create dispute on optimism/opstack chains when the optimism bridge is paused

## Summary
Severity: Medium
Chain: Smart contract
Component: Cross-chain-Realitio-Proxy
Published: 2025-09-27
Source: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/63
Type: hats-finding

## Details
**Github username:** --
  **Twitter username:** atharv_181
  **HATS Profile:** [HATS Profile](https://app.hats.finance/profile/Atharv181)

  **Beneficiary:** 0x6386B0A730C4Be11575B51A7DB93134a3D4d2ddF
  **Submission hash (on-chain):** 0xc2bf4757904939098ae25af8ac9d4ae634754075c071adae85cebb052d4b5428
  **Severity:** medium
  
  **Description:**
  **Description**\
Bridges of optimism chain can be paused by the guardian role, as can be seen from the docs [here](https://docs.optimism.io/stack/security/pause). 

The [superchainconfig code](https://github.com/ethereum-optimism/optimism/blob/856c08bf84d9aa829d1e764fc8e9a37d41960ba0/packages/contracts-bedrock/src/L1/SuperchainConfig.sol#L66-L71), where the guardian can pause the bridge.


The code of [CrossDomainMessenger.sol](https://etherscan.io/address/0x5d5a095665886119693f0b41d8dfee78da033e8b#code) where we have a function `relayMessage` which will be called after receiving the message from L2. It checks whether the bridge is paused or not here:

```solidity
         // On L1 this function will check the Portal for its paused status.
        // On L2 this function should be a no-op, because paused will always return false.
        require(paused() == false, "CrossDomainMessenger: paused");
```

This paused function is overridden in `L1CrossDomainMessenger` where it points to the superchainconfig and if the bridge is pause, it reverts.


Optimism bridge can be paused and even if we do a transaction on L2 to pass a message on L1 it will not revert as mentioned in the code `//On L2 this function should be a no-op, because paused will always return false.`, but reverts on L1.

Now consider a situation User requests for arbitration of questionId 1 and calls requestArbitration. This will call sendMessage and on L2 it calls `receiveArbitrationRequest`. This function notifies to realitio about the arbitration and calls `notifyOfArbitrationRequest`. At this point the status of the request is `Status.Notified`.

Now consider the bridge is paused but still malicious user calls the `handleNotifiedRequest` function and as can be seen above it will not revert and after the transaction status will be `Status.AwaitingRuling`. Because the bridge is paused on L1, contract will not receive any confirmation and hence it will not be able resolve dispute. 

Even after the bridge unpause, we cannot retry handleNotifiedRequest because the state required is `Notified` while we have `AwaitingRuling`. 

Another user cannot create a dispute for that question because on realitio side it is already notified and when notified again, it will revert and return failed status because the question id is already notified in realitio.


Hence, kleros will not be able to resolve the dispute in this case.

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Cross-chain-Realitio-Proxy-0x9efc47be23fb612aff9bce511bad4a308f1f4f39/issues/63_
