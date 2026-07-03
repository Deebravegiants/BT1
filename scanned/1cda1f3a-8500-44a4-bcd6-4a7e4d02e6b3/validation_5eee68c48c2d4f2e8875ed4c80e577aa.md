### Title
Missing `isEthDepositEnabled` Guard in `RSETHPoolV3ExternalBridge.deposit()` Bypasses Protocol-Wide ETH Deposit Disable — (File: contracts/pools/RSETHPoolV3ExternalBridge.sol)

---

### Summary

`RSETHPoolV3ExternalBridge.sol` omits the `isEthDepositEnabled` guard that is present in the sibling contracts `RSETHPoolV3.sol` and `RSETHPoolV3WithNativeChainBridge.sol`. This is a direct code-mismatch analog to the reported audit finding: one version of the logic carries a critical safety check; the deployed variant does not. Any depositor can continue minting wrsETH through `RSETHPoolV3ExternalBridge` even after the protocol has administratively disabled ETH deposits across all other pools.

---

### Finding Description

`RSETHPoolV3.sol` and `RSETHPoolV3WithNativeChainBridge.sol` both gate their ETH `deposit` path with:

```solidity
if (!isEthDepositEnabled) revert EthDepositDisabled();
``` [1](#0-0) [2](#0-1) 

`RSETHPoolV3ExternalBridge.sol` declares no `isEthDepositEnabled` state variable and its `deposit(string)` function contains no such guard:

```solidity
function deposit(string memory referralId)
    external
    payable
    nonReentrant
    whenNotPaused
    limitDailyMint(msg.value, ETH_IDENTIFIER)
{
    uint256 amount = msg.value;
    if (amount == 0) revert InvalidAmount();
    ...
    wrsETH.mint(msg.sender, rsETHAmount);
``` [3](#0-2) 

The storage layout of `RSETHPoolV3ExternalBridge` confirms the variable is entirely absent, not merely unchecked: [4](#0-3) 

The mismatch is structural: `RSETHPoolV3` carries `isEthDepositEnabled` as a first-class state variable and enforces it on every ETH deposit, while `RSETHPoolV3ExternalBridge` — which shares the same deposit-and-mint pattern — was written without it.

---

### Impact Explanation

When the protocol operator sets `isEthDepositEnabled = false` in `RSETHPoolV3` or `RSETHPoolV3WithNativeChainBridge` (e.g., during an oracle incident, a rate anomaly, or a planned upgrade), ETH deposits through those pools are blocked. However, `RSETHPoolV3ExternalBridge` has no corresponding control surface. Any depositor can call `deposit()` on `RSETHPoolV3ExternalBridge` and receive freshly minted wrsETH at whatever rate the oracle currently reports, regardless of the protocol's intent to halt minting.

If the disable was triggered because the rsETH/ETH oracle rate is temporarily unfavorable (too low), depositors who route through `RSETHPoolV3ExternalBridge` receive more wrsETH per ETH than they should, diluting existing holders. The protocol cannot stop this without pausing the entire contract — a coarser action that also blocks token deposits and bridging operations.

**Impact classification:** Low — Contract fails to deliver promised returns (the protocol's administrative control over ETH deposit enablement is not honored by this pool variant).

---

### Likelihood Explanation

The `isEthDepositEnabled` flag exists precisely because the protocol anticipates needing to toggle ETH deposits independently of a full pause. The flag is already wired into two of the three V3-family pools. The omission in `RSETHPoolV3ExternalBridge` is a copy-paste divergence of the kind described in the reference report. Any depositor who is aware of the discrepancy — or who simply tries the pool while others are disabled — can exploit it without any special privilege.

---

### Recommendation

Add `isEthDepositEnabled` as a state variable to `RSETHPoolV3ExternalBridge` and enforce it at the top of `deposit(string memory referralId)`, mirroring the pattern in `RSETHPoolV3`:

```solidity
if (!isEthDepositEnabled) revert EthDepositDisabled();
```

Provide a `setIsEthDepositEnabled` setter gated by `TIMELOCK_ROLE`, consistent with the sibling contracts. Maintain a single canonical implementation of the deposit guard and reference it across all pool variants to prevent future divergence.

---

### Proof of Concept

1. Operator calls `RSETHPoolV3.setIsEthDepositEnabled(false)` and `RSETHPoolV3WithNativeChainBridge.setIsEthDepositEnabled(false)` to halt ETH deposits protocol-wide.
2. Both pools now revert on `deposit()` with `EthDepositDisabled`.
3. Depositor calls `RSETHPoolV3ExternalBridge.deposit{value: 10 ether}("")`.
4. The call succeeds: no `isEthDepositEnabled` check exists, `limitDailyMint` and `whenNotPaused` pass, and `wrsETH.mint(msg.sender, rsETHAmount)` executes.
5. The depositor receives wrsETH at the current oracle rate while the protocol believed ETH deposits were disabled. [3](#0-2) [5](#0-4)

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L246-265)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        if (!isEthDepositEnabled) revert EthDepositDisabled();
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```

**File:** contracts/pools/RSETHPoolV3WithNativeChainBridge.sol (L289-289)
```text
        if (!isEthDepositEnabled) revert EthDepositDisabled();
```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L42-104)
```text
contract RSETHPoolV3ExternalBridge is ERC20Upgradeable, AccessControlUpgradeable, ReentrancyGuardUpgradeable {
    using SafeERC20 for IERC20;

    IERC20WrsETH public wrsETH;
    uint256 public feeBps; // Basis points for fees
    uint256 public feeEarnedInETH;
    address public rsETHOracle;

    bytes32 public constant BRIDGER_ROLE = keccak256("BRIDGER_ROLE");
    bytes32 public constant TIMELOCK_ROLE = keccak256("TIMELOCK_ROLE");

    /// @notice The corresponding L1Vault contract for the L2 chain
    address public l1VaultETHForL2Chain;
    /// @notice The StargatePool used for L2 --> L1 bridging
    IStargatePoolNative public stargatePool;
    /// @notice The LayerZero ID for the ETH mainnet
    uint32 public dstLzChainId;

    /// @notice The latest transaction receipt info from the StargatePoolNative
    TxReceipt public latestTxReceipt;

    /// @notice New variable added for pausable functionality
    bool public paused;

    /// @notice THe daily minting limit for rsETH
    uint256 public dailyMintLimit;

    /// @notice The amount of rsETH that was minted today
    uint256 public dailyMintAmount;

    /// @notice The last day that rsETH was minted
    uint256 public lastMintDay;

    /// @notice The start timestamp for the daily minting limit
    uint256 public startTimestamp;

    /// @notice ETH identifier address
    address public constant ETH_IDENTIFIER = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;

    /// @notice The mapping of token addresses to the fee earned in that token
    mapping(address token => uint256 feeEarned) public feeEarnedInToken;

    /// @notice The mapping of token addresses to their respective oracle addresses
    mapping(address token => address oracle) public supportedTokenOracle;

    /// @notice The mapping of token addresses to their respective token bridges
    mapping(address token => address bridge) public tokenBridge;

    /// @notice An array of supported token addresses
    address[] public supportedTokenList;

    /// @notice The pauser role identifier
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    /// @notice The address of the L2 bridge contract
    address public l2Bridge;

    /// @notice The address of the L2 messenger contract
    address public messenger;

    /// @notice The operator role identifier
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");

```

**File:** contracts/pools/RSETHPoolV3ExternalBridge.sol (L366-384)
```text
    function deposit(string memory referralId)
        external
        payable
        nonReentrant
        whenNotPaused
        limitDailyMint(msg.value, ETH_IDENTIFIER)
    {
        uint256 amount = msg.value;

        if (amount == 0) revert InvalidAmount();

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount);

        feeEarnedInETH += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);
    }
```
