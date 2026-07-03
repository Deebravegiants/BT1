Looking at the key contracts to assess this vulnerability claim.

### Title
Missing Recovery Function Causes Permanent Locking of OFT Decimal-Dust WETH in TACWETHBridge — (`contracts/bridges/TACWETHBridge.sol`)

---

### Summary

`TACWETHBridge` pulls the full user `amount` of WETH into itself, then calls `wethOFT.send()` which, per the LayerZero OFT standard, burns only `amountSentLD ≤ amountLD` (truncated to shared-decimal precision). The remainder `amount − amountSentLD` stays in the bridge contract. Unlike every other bridge contract in the codebase, `TACWETHBridge` inherits neither `Recoverable` nor any equivalent admin escape hatch, so this residual is permanently locked.

---

### Finding Description

In `bridgeTokenToL1`: [1](#0-0) 

The bridge pulls `amount` WETH from the caller into `address(this)`. [2](#0-1) 

`wethOFT.send()` is called with `amountLD: amount`. Per the LayerZero OFT standard, `send()` internally calls `_removeDust()` which truncates the amount to the nearest `10^(localDecimals − sharedDecimals)` unit before burning. The `OFTReceipt.amountSentLD` field is defined as: [3](#0-2) 

"Amount of tokens **ACTUALLY** debited from the sender in local decimals." When `sharedDecimals < 18` (the standard OFT configuration for WETH), `amountSentLD < amount` by up to `10^(18 − sharedDecimals)` wei per call. The difference remains as a balance in `TACWETHBridge`.

`TACWETHBridge` is declared as: [4](#0-3) 

It inherits only `AccessControl` and `ReentrancyGuard` — no `Recoverable`, no `recoverTokens`, no `emergencyRecover`. There is no function in the contract that can move an ERC-20 balance out.

By contrast, `SonicBridgeReceiver` — a sibling bridge contract — explicitly provides: [5](#0-4) 

And `Recoverable` provides a general-purpose admin escape hatch: [6](#0-5) 

`TACWETHBridge` has neither.

---

### Impact Explanation

Every call to `bridgeTokenToL1` leaves up to `10^(18 − sharedDecimals)` wei of WETH permanently locked in the bridge. For a typical OFT with 6 shared decimals this is up to `10^12` wei (≈ 0.000001 ETH) per transaction. The dust accumulates across all users and all calls with no mechanism for recovery. The funds are permanently frozen — no admin function, no upgrade path, no self-destruct.

Impact: **Permanent freezing of funds** (dust accumulation, not full principal loss per individual transaction, but irrecoverable in aggregate).

---

### Likelihood Explanation

This triggers on every single call to `bridgeTokenToL1` where `amount % 10^(18 − sharedDecimals) != 0`, which is the common case for arbitrary user-supplied amounts. No special attacker action is required; normal protocol usage is sufficient.

---

### Recommendation

Add `Recoverable` inheritance to `TACWETHBridge` (consistent with the rest of the codebase), or add a standalone `recoverTokens` admin function. Additionally, after calling `wethOFT.send()`, compare the pre/post WETH balance of the bridge and refund any dust to the caller:

```solidity
uint256 balanceBefore = IERC20(address(wethOFT)).balanceOf(address(this));
IERC20(address(wethOFT)).safeTransferFrom(msg.sender, address(this), amount);
(, OFTReceipt memory oftReceipt) = wethOFT.send{value: nativeFee}(sendParam, fee, msg.sender);
uint256 dust = IERC20(address(wethOFT)).balanceOf(address(this)) - balanceBefore;
if (dust > 0) IERC20(address(wethOFT)).safeTransfer(msg.sender, dust);
```

---

### Proof of Concept

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.27;

import {TACWETHBridge} from "contracts/bridges/TACWETHBridge.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract MockWETHOFT {
    mapping(address => uint256) public balanceOf;
    uint256 public constant DUST = 1e12; // 6 shared decimals

    function transfer(address to, uint256 amount) external returns (bool) {
        balanceOf[msg.sender] -= amount;
        balanceOf[to] += amount;
        return true;
    }
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        return true;
    }
    function quoteSend(bytes calldata, bool) external pure returns (uint256 nativeFee, uint256) {
        return (0.001 ether, 0);
    }
    // send() burns amountLD - DUST (simulating decimal truncation)
    function send(bytes calldata sendParam, bytes calldata, address)
        external payable returns (bytes memory, (uint256, uint256) memory)
    {
        uint256 amountLD = abi.decode(sendParam[64:96], (uint256));
        uint256 amountSentLD = amountLD - DUST;
        balanceOf[msg.sender] -= amountSentLD; // bridge loses amountSentLD
        return ("", (amountSentLD, amountSentLD));
    }
}

contract PoCTest {
    function test() external {
        MockWETHOFT oft = new MockWETHOFT();
        TACWETHBridge bridge = new TACWETHBridge(address(this), address(oft), 1, 100);

        // Fund user
        oft.balanceOf[address(this)] = 1 ether;

        // Call bridgeTokenToL1
        bridge.bridgeTokenToL1{value: 0.001 ether}(address(0x1234), 1 ether);

        // DUST remains locked in bridge, no recovery function exists
        assert(oft.balanceOf(address(bridge)) == 1e12);
        // No recoverTokens(), no emergencyRecover() — funds are permanently locked
    }
}
```

### Citations

**File:** contracts/bridges/TACWETHBridge.sol (L16-16)
```text
contract TACWETHBridge is IL2TokenBridge, AccessControl, ReentrancyGuard {
```

**File:** contracts/bridges/TACWETHBridge.sol (L116-116)
```text
        IERC20(address(wethOFT)).safeTransferFrom(msg.sender, address(this), amount);
```

**File:** contracts/bridges/TACWETHBridge.sol (L131-131)
```text
        (, OFTReceipt memory oftReceipt) = wethOFT.send{ value: nativeFee }(sendParam, fee, msg.sender);
```

**File:** contracts/external/layerzero/interfaces/IOFT.sol (L37-40)
```text
struct OFTReceipt {
    uint256 amountSentLD; // Amount of tokens ACTUALLY debited from the sender in local decimals
    uint256 amountReceivedLD; // Amount of tokens to be received on the remote side
}
```

**File:** contracts/bridges/SonicBridgeReceiver.sol (L164-172)
```text
    function emergencyRecover(address token, address recipient, uint256 amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        UtilLib.checkNonZeroAddress(recipient);

        uint256 balance = IERC20(token).balanceOf(address(this));
        uint256 recoverAmount = amount == 0 ? balance : amount;
        if (recoverAmount > balance) revert InsufficientBalance();

        IERC20(token).safeTransfer(recipient, recoverAmount);
    }
```

**File:** contracts/utils/Recoverable.sol (L41-57)
```text
    function recoverTokens(
        address tokenAddress,
        address recipient,
        uint256 amount
    )
        external
        onlyRole(DEFAULT_ADMIN_ROLE)
    {
        UtilLib.checkNonZeroAddress(tokenAddress);
        UtilLib.checkNonZeroAddress(recipient);
        if (amount == 0) revert ZeroAmount();
        if (IERC20(tokenAddress).balanceOf(address(this)) < amount) revert InsufficientBalance();

        IERC20(tokenAddress).safeTransfer(recipient, amount);

        emit TokensRecovered(tokenAddress, recipient, amount);
    }
```
