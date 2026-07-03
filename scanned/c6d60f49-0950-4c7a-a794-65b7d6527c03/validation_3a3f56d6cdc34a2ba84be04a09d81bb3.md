### Title
CCIP Fee Staleness via Block Stuffing Causes Repeated Revert in `bridgeRsETHToL2UsingCCIP` — (`contracts/L1VaultV2.sol`)

---

### Summary

`bridgeRsETHToL2UsingCCIP()` fetches the CCIP fee internally at execution time and enforces an exact match against `msg.value`. Because the manager must pre-compute the fee off-chain before submitting the transaction, an attacker who stuffs blocks between the off-chain fee query and the on-chain call can cause the fee to shift, making the transaction revert with `IncorrectCCIPFee`. The rsETH minted in the prior step remains stranded in `L1VaultV2` until the manager successfully retries.

---

### Finding Description

The three-step WETH→rsETH→L2 pipeline in `L1VaultV2` is intentionally split across separate manager transactions:

1. `unwrapWETH()` — calls `IWETH(WETH).withdraw(wethBalance)`, converting WETH to ETH. [1](#0-0) 

2. `depositETHForL1VaultETH()` — deposits the ETH into `lrtDepositPool` to mint rsETH. [2](#0-1) 

3. `bridgeRsETHToL2UsingCCIP()` — bridges the rsETH to L2 via Chainlink CCIP. [3](#0-2) 

The critical design point is inside step 3: the fee is **re-fetched at execution time** and compared against `msg.value` with an exact equality check:

```solidity
uint256 fee = getCCIPFee(amount);   // fetched on-chain at execution time
if (msg.value != fee) {
    revert IncorrectCCIPFee();
}
``` [4](#0-3) 

`getCCIPFee()` delegates to `ccipRouter.getFee()`, whose return value is determined by the CCIP router's current gas-price oracle for the destination chain: [5](#0-4) 

The manager must call `getCCIPFee()` off-chain, then submit `bridgeRsETHToL2UsingCCIP{value: fee}(amount)`. If an attacker stuffs blocks between the off-chain query and the on-chain inclusion, the CCIP router's fee can shift, causing the exact-match check to fail and the transaction to revert. The attacker can repeat this for every retry, keeping rsETH stranded in `L1VaultV2`.

---

### Impact Explanation

**Low — Block stuffing.** rsETH minted in step 2 is temporarily frozen inside `L1VaultV2`. No funds are lost; the manager can eventually retry when block stuffing stops. However, the pipeline has no on-chain atomicity guarantee and no tolerance window on the fee check, so a sustained block-stuffing campaign can delay bridging indefinitely.

---

### Likelihood Explanation

Low. Block stuffing on Ethereum mainnet is economically expensive (the attacker must outbid all legitimate transactions for every block they fill). The attack is realistic only when the value of the rsETH being bridged justifies the cost, or when the attacker has an off-chain incentive to delay the bridge. The CCIP fee must also actually change during the stuffed window, which depends on destination-chain gas volatility.

---

### Recommendation

Replace the exact-equality fee check with a caller-supplied maximum fee and pass any surplus back, or accept a `maxFee` parameter and allow `msg.value >= fee`:

```solidity
// Accept up to maxFee; refund excess
uint256 fee = getCCIPFee(amount);
if (msg.value < fee) revert IncorrectCCIPFee();
// refund surplus
if (msg.value > fee) {
    (bool ok,) = msg.sender.call{value: msg.value - fee}("");
    require(ok);
}
```

This eliminates the exact-match window entirely: the manager can supply a slightly higher `msg.value` as a buffer, and the transaction succeeds even if the fee ticks up by a small amount between query and inclusion.

---

### Proof of Concept

Fork-test outline (local/private testnet, no public-mainnet execution):

```solidity
// 1. Deploy L1VaultV2 with BridgeType.CCIP and a mock CCIP router
// 2. Fund vault with WETH; manager calls unwrapWETH() → ETH in vault
// 3. Manager calls depositETHForL1VaultETH() → rsETH minted
// 4. Mock router: record fee G at block N
// 5. vm.roll(N + stuffedBlocks); mock router now returns G' > G
// 6. Manager calls bridgeRsETHToL2UsingCCIP{value: G}(amount)
// 7. Assert: revert IncorrectCCIPFee
// 8. Assert: rsETH.balanceOf(vault) == amount (funds stranded)
```

The mock router's `getFee()` returns `G` before the roll and `G'` after, simulating a fee change across the stuffed block range. The revert on step 6 confirms the invariant break.

### Citations

**File:** contracts/L1VaultV2.sol (L224-235)
```text
    function depositETHForL1VaultETH() external payable nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 balanceOfETH = address(this).balance;
        uint256 rsETHAmountToMint = lrtDepositPool.getRsETHAmountToMint(ETH_IDENTIFIER, balanceOfETH);

        if (rsETHAmountToMint == 0) {
            revert InvalidMinRSETHAmountExpected();
        }

        lrtDepositPool.depositETH{ value: balanceOfETH }(rsETHAmountToMint, "");

        emit ETHDepositForL1Vault(balanceOfETH, rsETHAmountToMint);
    }
```

**File:** contracts/L1VaultV2.sol (L273-284)
```text
    function unwrapWETH() external nonReentrant onlyRole(MANAGER_ROLE) {
        uint256 wethBalance = IERC20(WETH).balanceOf(address(this));

        if (wethBalance == 0) {
            revert NoWETHBalance();
        }

        // Unwrap WETH to ETH
        IWETH(WETH).withdraw(wethBalance);

        emit WETHUnwrapped(wethBalance);
    }
```

**File:** contracts/L1VaultV2.sol (L341-367)
```text
    function bridgeRsETHToL2UsingCCIP(uint256 amount) external payable nonReentrant onlyRole(MANAGER_ROLE) {
        if (bridgeType != BridgeType.CCIP) {
            revert InactiveBridgeType();
        }

        if (rsETH.balanceOf(address(this)) < amount) {
            revert InsufficientRsETHBalance();
        }

        if (amount == 0) {
            revert ZeroAmount();
        }

        uint256 fee = getCCIPFee(amount);

        if (msg.value != fee) {
            revert IncorrectCCIPFee();
        }

        IERC20(address(rsETH)).safeIncreaseAllowance(address(ccipRouter), amount);

        Client.EVM2AnyMessage memory message = getCCIPMessage(amount);

        bytes32 messageId = ccipRouter.ccipSend{ value: msg.value }(destinationChainSelector, message);

        emit BridgedRsETHToL2UsingCCIP(destinationChainSelector, l2Receiver, amount, messageId);
    }
```

**File:** contracts/L1VaultV2.sol (L400-404)
```text
    function getCCIPFee(uint256 amount) public view returns (uint256) {
        Client.EVM2AnyMessage memory message = getCCIPMessage(amount);

        return ccipRouter.getFee(destinationChainSelector, message);
    }
```
