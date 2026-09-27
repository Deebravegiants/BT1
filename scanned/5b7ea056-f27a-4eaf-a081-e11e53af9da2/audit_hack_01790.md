# [M] Router - Cancel is not implemented

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
#### Description

Canceling of failed/expired swaps does not seem to be implemented in the router. This may allow a user to trick the router into preparing all its funds which will not automatically be reclaimed after expiration (router DoS).

#### Examples

* cancelExpired is never called


**code/packages/sdk/src/sdk.ts:L873-L885**
```solidity
// TODO: this just cancels a transaction, it is misnamed, has nothing to do with expiries
public async cancelExpired(cancelParams: CancelParams, chainId: number): Promise<providers.TransactionResponse> {
  const method = this.cancelExpired.name;
  const methodId = getRandomBytes32();
  this.logger.info({ method, methodId, cancelParams, chainId }, "Method started");
  const cancelRes = await this.transactionManager.cancel(chainId, cancelParams);
  if (cancelRes.isOk()) {
    this.logger.info({ method, methodId }, "Method complete");
    return cancelRes.value;
  } else {
    throw cancelRes.error;
  }
}
```

* disabled code


**code/packages/router/src/handler.ts:L719-L733**
```solidity
  "Do not cancel ATM, figure out why we are in this case first",
);
// const cancelRes = await this.txManager.cancel(txData.sendingChainId, {
//   txData,
//   signature: "0x",
//   relayerFee: "0",
// });
// if (cancelRes.isOk()) {
//   this.logger.warn(
//     { method, methodId, transactionHash: cancelRes.value.transactionHash },
//     "Cancelled transaction",
//   );
// } else {
//   this.logger.error({ method, methodId }, "Could not cancel transaction after error!");
// }
```

#### Recommendation

Implement the cancel flow.
