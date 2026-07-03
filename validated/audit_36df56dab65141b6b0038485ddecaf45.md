### Title
ERC20 Tokens Sent to `FeeReceiver` Are Permanently Locked — (`contracts/FeeReceiver.sol`)

### Summary
`FeeReceiver` is the designated fee recipient for MEV and execution-layer rewards. It accepts ETH via a bare `receive()` and forwards it to the deposit pool through `sendFunds()`. However, the contract contains no function to transfer ERC20 tokens out. Any ERC20 tokens that arrive at this address — whether sent accidentally, routed there by an MEV bundle, or transferred by any external caller — are permanently locked with no on-chain recovery path.

### Finding Description
`FeeReceiver.sol` exposes only two mechanisms for moving value:

1. `receive() external payable {}` — accepts ETH silently.
2. `sendFunds()` — reads `address(this).balance` and forwards it to `ILRTDepositPool.receiveFromRewardReceiver`. [1](#0-0) 

There is no `sweepToken`, `rescueERC20`, or any other function that reads an ERC20 balance and transfers it out. The entire contract body is: [2](#0-1) 

Any ERC20 token transferred to this address — stETH, ETH-rebasing tokens, arbitrary ERC20s from MEV bundles, or tokens sent by mistake — has no on-chain exit path.

### Impact Explanation
ERC20 tokens that arrive at `FeeReceiver` are permanently frozen at the contract address. Because `sendFunds()` only reads `address(this).balance` (native ETH), token balances are never touched. The tokens cannot be forwarded to the deposit pool, swept to treasury, or recovered by any role. This constitutes **permanent freezing of unclaimed yield** (protocol-level rewards that should flow into the TVL but instead sit inert).

The contract is upgradeable (`Initializable` + proxy pattern), so a governance upgrade could add a rescue function — identical to the mitigating factor acknowledged in the original M-13 report. This is why the severity is Medium rather than Critical.

### Likelihood Explanation
The `FeeReceiver` address is set as the `fee_recipient` for Kelp's validators. In the current MEV-boost ecosystem, MEV bundles routinely include ERC20 token transfers (e.g., arbitrage profits, liquidation proceeds) alongside ETH payments. While the ETH component goes to `address(this).balance`, ERC20 tokens transferred to the fee recipient within the same bundle land in the contract's token balance with no recovery path. Additionally, any user or protocol participant can directly `transfer` ERC20 tokens to this address, and the contract silently accepts them.

### Recommendation
Add a governance-restricted sweep function:

```solidity
function sweepToken(address token, address recipient) external onlyRole(LRTConstants.MANAGER) {
    uint256 balance = IERC20(token).balanceOf(address(this));
    if (balance == 0) revert InvalidEmptyValue();
    IERC20(token).safeTransfer(recipient, balance);
}
```

This mirrors the recommendation in M-13 and is consistent with the `sweepRemainingAssets` pattern already present in `LRTWithdrawalManager`. [3](#0-2) 

### Proof of Concept

1. The Kelp protocol sets `FeeReceiver` as the `fee_recipient` for its validators.
2. An MEV searcher submits a bundle that includes a direct ERC20 `transfer` to the `FeeReceiver` address (e.g., as a bribe or as part of an arbitrage path).
3. The ERC20 tokens land in `FeeReceiver`'s balance.
4. Any caller invokes `sendFunds()` — only `address(this).balance` (ETH) is forwarded; the ERC20 balance is untouched.
5. No role (`DEFAULT_ADMIN_ROLE`, `MANAGER`) has any function available to move the ERC20 tokens.
6. The tokens remain locked indefinitely until a contract upgrade adds a rescue path. [4](#0-3)

### Citations

**File:** contracts/FeeReceiver.sol (L1-73)
```text
// SPDX-License-Identifier: BUSL-1.1
pragma solidity 0.8.27;

import { Initializable } from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import { AccessControlUpgradeable } from "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import { LRTConstants } from "./utils/LRTConstants.sol";
import { ILRTDepositPool } from "./interfaces/ILRTDepositPool.sol";
import { IFeeReceiver } from "./interfaces/IFeeReceiver.sol";

/// @title FeeReceiver
/// @notice Receives Mev/Execution-layer rewards
/// @dev also known as RewardReceiver Contract in LRTConstants.sol
contract FeeReceiver is IFeeReceiver, Initializable, AccessControlUpgradeable {
    address public _legacyProtocolTreasury;
    address public depositPool;
    uint256 public _legacyProtocolFeePercentInBPS;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(
        address _protocolTreasury,
        address _depositPool,
        uint256 _protocolFeePercentInBPS,
        address admin,
        address manager
    )
        external
        initializer
    {
        if (
            _protocolTreasury == address(0) || _depositPool == address(0) || _protocolFeePercentInBPS == 0
                || admin == address(0) || manager == address(0)
        ) {
            revert InvalidEmptyValue();
        }

        _legacyProtocolTreasury = _protocolTreasury;
        depositPool = _depositPool;
        _legacyProtocolFeePercentInBPS = _protocolFeePercentInBPS;

        __AccessControl_init();
        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(LRTConstants.MANAGER, manager);
    }

    /// @dev fallback to receive funds
    receive() external payable { }

    /// @dev send all rewards to deposit pool
    function sendFunds() external {
        uint256 balance = address(this).balance;
        ILRTDepositPool(depositPool).receiveFromRewardReceiver{ value: balance }();

        emit MevRewardsAddedToTVL(balance);
    }

    /*//////////////////////////////////////////////////////////////
                            MANAGER FUNCTIONS
    //////////////////////////////////////////////////////////////*/

    /// @dev Set the deposit pool
    /// @param _depositPool Address of the deposit pool
    function setDepositPool(address _depositPool) external onlyRole(LRTConstants.MANAGER) {
        if (_depositPool == address(0)) revert InvalidEmptyValue();

        depositPool = _depositPool;

        emit DepositPoolSet(_depositPool);
    }
}
```

**File:** contracts/LRTWithdrawalManager.sol (L395-414)
```text
    function sweepRemainingAssets(address asset)
        external
        nonReentrant
        onlySupportedAsset(asset)
        onlyLRTManager
        returns (uint256 transferredAmount)
    {
        // Check that all withdrawals are completed
        if (hasUnlockedWithdrawals(asset)) revert PendingWithdrawalsExist();

        uint256 balance = _getAssetBalance(asset);
        if (balance == 0) revert AmountMustBeGreaterThanZero();

        // Transfer to treasury
        address treasury = lrtConfig.getContract(LRTConstants.PROTOCOL_TREASURY);
        _transferAsset(asset, treasury, balance);

        emit RemainingAssetsSwept(asset, balance, treasury);
        return balance;
    }
```
