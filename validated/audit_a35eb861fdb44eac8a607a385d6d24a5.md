### Title
Unconditional `onERC721Received` Allows Operator to Claim Third-Party Lido Withdrawal NFTs, Stealing ETH — (`contracts/LRTConverter.sol`)

---

### Summary

`LRTConverter` accepts **any** ERC-721 token unconditionally via `onERC721Received`. Because `claimStEth` contains no guard verifying that a given `_requestId` was created by this contract's own `unstakeStEth` calls, an operator (including an automated claiming script) can claim a third-party Lido withdrawal NFT that was transferred to the converter, sweeping the ETH proceeds into the protocol's TVL.

---

### Finding Description

**Step 1 — Unconditional NFT acceptance.**

`onERC721Received` returns the selector for every caller and every token ID with no validation: [1](#0-0) 

This means any `safeTransferFrom` of a Lido withdrawal queue NFT to `LRTConverter` will succeed and leave the contract as the NFT's owner.

**Step 2 — No provenance check in `claimStEth`.**

`claimStEth` accepts an arbitrary `_requestId` supplied by the operator and immediately forwards it to `_claimStEth`: [2](#0-1) 

There is no mapping, set, or any other on-chain record of which request IDs were created by this contract's own `_unstakeStEth` calls. The only thing emitted is an event: [3](#0-2) 

**Step 3 — Lido claim succeeds because the contract is now the NFT owner.**

`_claimStEth` calls `claimWithdrawalsTo` with `address(this)` as recipient. Lido's withdrawal queue authorises the claim based on NFT ownership; since `LRTConverter` now owns the third-party NFT, the call succeeds: [4](#0-3) 

**Step 4 — Full ETH balance swept to deposit pool.**

After the claim, `_sendEthToDepositPool(address(this).balance)` sends **all** ETH held by the contract (including the just-claimed third-party ETH) to the protocol deposit pool: [5](#0-4) 

The third party's ETH is permanently absorbed into the protocol's TVL.

---

### Impact Explanation

The third-party NFT owner loses both their stETH principal and any accrued yield. The ETH is not locked — it is actively redistributed into the protocol's deposit pool, benefiting rsETH holders at the victim's expense. This matches **High — Theft of unclaimed yield** (and principal).

---

### Likelihood Explanation

- Any operator running an automated claiming script that iterates over all Lido NFTs held by the contract (a natural operational pattern) will inadvertently claim third-party NFTs without needing to be malicious.
- A third party might accidentally `safeTransferFrom` their NFT to the converter (e.g., copy-paste error, UI bug, or deliberate griefing setup).
- No special permissions beyond the `LRT_OPERATOR` role are required, and that role is expected to call `claimStEth` regularly.

---

### Recommendation

1. **Track self-owned request IDs.** In `_unstakeStEth`, store each returned `requestId` in a `mapping(uint256 => bool) private _ownedRequestIds` (or an `EnumerableSet`).
2. **Guard `_claimStEth`.** Revert if `_requestId` is not in `_ownedRequestIds`; delete it after a successful claim.
3. **Restrict `onERC721Received`.** Only accept transfers from the Lido withdrawal queue address (`msg.sender == address(withdrawalQueue)`), rejecting all other ERC-721 tokens.

---

### Proof of Concept

```solidity
// Fork test (Ethereum mainnet fork)
// 1. Alice owns a finalized Lido withdrawal NFT (requestId = X, worth 10 ETH).
// 2. Alice calls: lidoWithdrawalQueue.safeTransferFrom(alice, address(lrtConverter), X)
//    → onERC721Received returns selector; LRTConverter is now owner of NFT X.
// 3. Operator calls: lrtConverter.claimStEth(X, hint)
//    → _claimStEth: withdrawalQueue.claimWithdrawalsTo([X], [hint], address(lrtConverter))
//      succeeds because lrtConverter owns NFT X.
//    → lrtConverter receives 10 ETH.
//    → _sendEthToDepositPool(address(lrtConverter).balance) sends 10 ETH to deposit pool.
// 4. Assert: alice's ETH is gone; lrtConverter.balance == 0; depositPool received 10 ETH.
```

### Citations

**File:** contracts/LRTConverter.sol (L113-115)
```text
    function onERC721Received(address, address, uint256, bytes calldata) external pure returns (bytes4) {
        return this.onERC721Received.selector;
    }
```

**File:** contracts/LRTConverter.sol (L180-183)
```text
    function claimStEth(uint256 _requestId, uint256 _hint) external nonReentrant onlyLRTOperator {
        _claimStEth(_requestId, _hint);
        _sendEthToDepositPool(address(this).balance);
    }
```

**File:** contracts/LRTConverter.sol (L252-262)
```text
    function _sendEthToDepositPool(uint256 _amount) internal {
        address lrtDepositPoolAddress = lrtConfig.getContract(LRTConstants.LRT_DEPOSIT_POOL);

        if (ethValueInWithdrawal > _amount) {
            ethValueInWithdrawal -= _amount;
        } else {
            ethValueInWithdrawal = 0;
        }
        // Send eth to deposit pool
        ILRTDepositPool(lrtDepositPoolAddress).receiveFromLRTConverter{ value: _amount }();
        emit EthTransferred(lrtDepositPoolAddress, _amount);
```

**File:** contracts/unstaking-adapters/UnstakeStETH.sol (L54-56)
```text
        uint256[] memory requestIds = withdrawalQueue.requestWithdrawals(amounts, address(this));

        emit UnstakeStETHStarted(requestIds[0]);
```

**File:** contracts/unstaking-adapters/UnstakeStETH.sol (L59-65)
```text
    function _claimStEth(uint256 _requestId, uint256 _hint) internal {
        uint256[] memory requestIds = new uint256[](1);
        uint256[] memory hints = new uint256[](1);
        requestIds[0] = _requestId;
        hints[0] = _hint;
        withdrawalQueue.claimWithdrawalsTo(requestIds, hints, address(this));
    }
```
