Audit Report

## Title
`claimStEth`/`claimSwEth` Pass Full Contract Balance to `_sendEthToDepositPool`, Over-Decrementing `ethValueInWithdrawal` and Understating rsETH Price - (File: contracts/LRTConverter.sol)

## Summary
`LRTConverter.claimStEth` and `claimSwEth` pass `address(this).balance` to `_sendEthToDepositPool` rather than only the ETH received from the specific claim. Because `LRTConverter` has a public payable `receive()` function, any ETH present in the contract from external sources is swept along with the claim proceeds, causing `ethValueInWithdrawal` to be decremented by more than the actual claim amount. The resulting understatement of `ethValueInWithdrawal` propagates through `getETHDistributionData` → `getTotalAssetDeposits` → `_getTotalEthInProtocol` → rsETH price, allowing new depositors to mint rsETH at a discount and diluting existing holders.

## Finding Description

`LRTConverter` tracks the ETH value of assets in the unstaking pipeline via `ethValueInWithdrawal`. It is incremented in `transferAssetFromDepositPool` and decremented inside `_sendEthToDepositPool`.

Both claim functions pass the full contract balance:

```solidity
// contracts/LRTConverter.sol L180-183
function claimStEth(uint256 _requestId, uint256 _hint) external nonReentrant onlyLRTOperator {
    _claimStEth(_requestId, _hint);
    _sendEthToDepositPool(address(this).balance);  // full balance, not just claim proceeds
}

// contracts/LRTConverter.sol L191-194
function claimSwEth(uint256 _tokenId) external nonReentrant onlyLRTOperator {
    _claimSwEth(_tokenId);
    _sendEthToDepositPool(address(this).balance);  // full balance, not just claim proceeds
}
```

`_claimStEth` calls `withdrawalQueue.claimWithdrawalsTo(requestIds, hints, address(this))`, sending Lido's ETH directly to `LRTConverter`. `_claimSwEth` calls `swEXIT.finalizeWithdrawal(_tokenId)`, which similarly delivers ETH to `address(this)`. After either call, `address(this).balance` equals the claim proceeds **plus** any ETH already sitting in the contract.

Inside `_sendEthToDepositPool`, the passed amount is used to decrement `ethValueInWithdrawal`:

```solidity
// contracts/LRTConverter.sol L252-263
function _sendEthToDepositPool(uint256 _amount) internal {
    ...
    if (ethValueInWithdrawal > _amount) {
        ethValueInWithdrawal -= _amount;
    } else {
        ethValueInWithdrawal = 0;
    }
    ILRTDepositPool(lrtDepositPoolAddress).receiveFromLRTConverter{ value: _amount }();
    ...
}
```

The `else` branch prevents arithmetic underflow but does not prevent the over-decrement: if pre-existing ETH inflates `_amount`, `ethValueInWithdrawal` is set to 0 while legitimate pending withdrawals remain, or is decremented by more than the actual claim amount.

The public payable `receive()` at L117-118 is the entry point for any address to deposit ETH into the contract without any accounting update:

```solidity
// contracts/LRTConverter.sol L117-118
receive() external payable { }
```

`ethValueInWithdrawal` is read by `getETHDistributionData` as `ethLyingInConverter` (L498-499), which feeds into `getTotalAssetDeposits` (L385-397), which is consumed by `_getTotalEthInProtocol` in `LRTOracle` (L331-349), which determines the rsETH price (L250).

## Impact Explanation

When `ethValueInWithdrawal` is over-decremented, `_getTotalEthInProtocol()` returns a lower figure than the true protocol TVL. The rsETH price computed from this understated TVL is lower than it should be. New depositors who call `depositETH` or `depositAsset` during this window receive more rsETH per ETH than they are entitled to, diluting the share of existing rsETH holders. The ETH that entered the contract via `receive()` should have accrued as yield to existing holders (increasing the rsETH price), but instead it is effectively redistributed to new minters at the expense of existing holders.

**Impact: High — Theft of unclaimed yield.**

## Likelihood Explanation

The precondition is that `LRTConverter` holds ETH from a source other than the specific claim being processed. The `receive()` function is public and payable, so any address can send ETH to the contract at any time — accidentally (wrong address), via `selfdestruct` proceeds, or by MEV bots. Once ETH is present, the next routine operator call to `claimStEth` or `claimSwEth` (normal protocol operation, not a compromise) triggers the accounting error. The operator is not acting maliciously; the bug is in the code. Deliberate exploitation is not self-profitable (the attacker loses the donated ETH), but the condition can arise accidentally.

**Likelihood: Low.**

## Recommendation

Capture the balance before the claim and pass only the delta to `_sendEthToDepositPool`:

```diff
  function claimStEth(uint256 _requestId, uint256 _hint) external nonReentrant onlyLRTOperator {
+     uint256 balanceBefore = address(this).balance;
      _claimStEth(_requestId, _hint);
-     _sendEthToDepositPool(address(this).balance);
+     _sendEthToDepositPool(address(this).balance - balanceBefore);
  }

  function claimSwEth(uint256 _tokenId) external nonReentrant onlyLRTOperator {
+     uint256 balanceBefore = address(this).balance;
      _claimSwEth(_tokenId);
-     _sendEthToDepositPool(address(this).balance);
+     _sendEthToDepositPool(address(this).balance - balanceBefore);
  }
```

This ensures `ethValueInWithdrawal` is decremented only by the ETH actually received from the specific claim, and any pre-existing ETH in the contract is not swept or double-counted.

## Proof of Concept

1. Protocol state: 100 ETH of stETH is in Lido's withdrawal queue across two requests (50 ETH each); `ethValueInWithdrawal = 100 ETH`. Deposit pool holds 0 ETH.
2. An external address sends 10 ETH directly to `LRTConverter` via `receive()`. `address(this).balance = 10 ETH`. This ETH is not counted in `ethValueInWithdrawal` or anywhere else in the TVL.
3. Operator calls `claimStEth(requestId, hint)` for the first 50 ETH Lido request. Lido sends 50 ETH to `LRTConverter`. `address(this).balance = 60 ETH`.
4. `_sendEthToDepositPool(60)` is called. `ethValueInWithdrawal = 100 - 60 = 40 ETH` (correct value would be `100 - 50 = 50 ETH`). 60 ETH is forwarded to the deposit pool.
5. Protocol TVL is now: `ethLyingInConverter = 40 ETH` + `ethLyingInDepositPool = 60 ETH` = 100 ETH. The correct TVL is `50 + 60 = 110 ETH` — the 10 ETH donation is now in the pool but `ethValueInWithdrawal` was over-decremented by 10 ETH, netting a 10 ETH undercount.
6. rsETH price is understated. Any depositor who calls `depositETH` before the remaining 50 ETH Lido claim is processed receives more rsETH than entitled, diluting existing holders by the 10 ETH that should have accrued as yield.

**Foundry test plan:** Deploy `LRTConverter` with mocked Lido withdrawal queue and deposit pool. Set `ethValueInWithdrawal = 100 ether`. Send 10 ETH to `LRTConverter` via `address(converter).call{value: 10 ether}("")`. Mock the Lido claim to deliver 50 ETH. Call `claimStEth`. Assert `ethValueInWithdrawal == 40 ether` (demonstrating the over-decrement vs. expected `50 ether`). Assert deposit pool received 60 ETH. Compute rsETH price before and after; assert it is lower than the correct price computed with `ethValueInWithdrawal = 50 ether`.