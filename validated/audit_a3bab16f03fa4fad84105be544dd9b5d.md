The full contract is confirmed. There is no length validation on `referralId` anywhere in `RSETHPoolV3.sol`. Here is the complete analysis:

---

### Title
Unbounded `referralId` String Enables Unbounded Gas Consumption Per Deposit — (`contracts/pools/RSETHPoolV3.sol`)

### Summary
Both `deposit` overloads in `RSETHPoolV3` accept a caller-controlled `string memory referralId` with no length bound. The string is copied into memory and emitted verbatim in a log. Because EVM gas scales linearly (and memory expansion quadratically) with string length, a single deposit call can consume an arbitrarily large amount of gas, bounded only by the block gas limit.

### Finding Description
`deposit(string memory referralId)` and `deposit(address, uint256, string memory referralId)` both accept an unbounded string parameter. [1](#0-0) [2](#0-1) 

Neither function validates `bytes(referralId).length`. The string is passed directly to:

```solidity
emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId);       // line 264
emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token); // line 292
``` [3](#0-2) 

Gas costs that scale with `len(referralId)`:

| Component | Cost |
|---|---|
| Calldata (non-zero bytes) | 16 gas/byte (EIP-2028) |
| Memory allocation | ~3 gas/word + quadratic expansion |
| LOG data | 8 gas/byte |

There is no guard — not `nonReentrant`, not `whenNotPaused`, not `limitDailyMint` — that caps the string length. [4](#0-3) 

### Impact Explanation
An attacker submits `deposit{value: 1 wei}(referralId = bytes(L))` where `L` is chosen so that total gas consumed approaches the L2 block gas limit `B`. Because L2 block gas limits are typically 30–32 M gas (Optimism/Arbitrum), and calldata alone costs 16 gas/byte, a string of ~1.8 M non-zero bytes suffices to fill a block. The attacker:

1. Pays only 1 wei ETH (receives rsETH back) plus gas fees.
2. Leaves insufficient gas for any other transaction in the same block.
3. Can repeat every block at minimal cost.

This constitutes **unbounded gas consumption** (the contract imposes no ceiling on per-call gas) and **block stuffing** (the block is monopolized by a single caller).

### Likelihood Explanation
- No privilege required — any EOA can call `deposit`.
- Minimum ETH cost is 1 wei per block.
- On L2s where this contract is deployed, gas fees are low, making sustained attacks economically viable.
- The attack path is direct: one function call, no setup, no oracle manipulation.

### Recommendation
Add a maximum length check at the top of both `deposit` functions:

```solidity
uint256 constant MAX_REFERRAL_ID_LENGTH = 128; // or any reasonable bound

function deposit(string memory referralId) external payable ... {
    if (bytes(referralId).length > MAX_REFERRAL_ID_LENGTH) revert ReferralIdTooLong();
    ...
}
```

Apply the same guard to `deposit(address, uint256, string memory referralId)`.

### Proof of Concept

```solidity
// Foundry fork test (local fork, no mainnet)
function testUnboundedReferralIdGriefing() public {
    // Fund attacker
    vm.deal(attacker, 1 ether);

    // Build a referralId that approaches the block gas limit
    // Arbitrum block gas limit ~32M; calldata ~16 gas/byte => ~1.8M bytes
    string memory hugeId = new string(1_800_000);
    bytes memory b = bytes(hugeId);
    for (uint i = 0; i < b.length; i++) b[i] = 0x41; // non-zero bytes

    uint256 gasBefore = gasleft();
    vm.prank(attacker);
    pool.deposit{value: 1 wei}(string(b));
    uint256 gasUsed = gasBefore - gasleft();

    // Assert gas consumed is near block limit
    assertGt(gasUsed, 25_000_000);

    // Assert a normal deposit now fails due to insufficient remaining gas
    vm.prank(normalUser);
    vm.deal(normalUser, 1 ether);
    // This call would revert or be excluded from the block
    (bool success,) = address(pool).call{value: 1 ether, gas: gasleft()}(
        abi.encodeWithSignature("deposit(string)", "normal")
    );
    assertFalse(success); // insufficient gas remains
}
```

### Citations

**File:** contracts/pools/RSETHPoolV3.sol (L96-125)
```text
    modifier limitDailyMint(uint256 amount, address token) {
        if (block.timestamp < startTimestamp) {
            revert MintBeforeStartTimestamp();
        }

        uint256 rsETHAmount;

        // Calculate the amount of rsETH that will be minted
        if (token == ETH_IDENTIFIER) {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount);
        } else {
            (rsETHAmount,) = viewSwapRsETHAmountAndFee(amount, token);
        }

        uint256 currentDay = getCurrentDay();

        // If the current day is greater than the last mint day, reset the daily mint amount
        if (currentDay > lastMintDay) {
            lastMintDay = currentDay;
            dailyMintAmount = 0;
        }

        // Check if the daily mint amount plus the amount to mint is greater than the daily mint limit
        if (dailyMintAmount + rsETHAmount > dailyMintLimit) {
            revert DailyMintLimitExceeded();
        }

        dailyMintAmount += rsETHAmount;
        _;
    }
```

**File:** contracts/pools/RSETHPoolV3.sol (L150-153)
```text
    event SwapOccurred(address indexed user, uint256 rsETHAmount, uint256 fee, string referralId);
    event SwapOccurred(
        address indexed user, uint256 rsETHAmount, uint256 fee, string referralId, address indexed token
    );
```

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

**File:** contracts/pools/RSETHPoolV3.sol (L271-293)
```text
    function deposit(
        address token,
        uint256 amount,
        string memory referralId
    )
        external
        nonReentrant
        whenNotPaused
        onlySupportedToken(token)
        limitDailyMint(amount, token)
    {
        if (amount == 0) revert InvalidAmount();

        IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

        (uint256 rsETHAmount, uint256 fee) = viewSwapRsETHAmountAndFee(amount, token);

        feeEarnedInToken[token] += fee;

        wrsETH.mint(msg.sender, rsETHAmount);

        emit SwapOccurred(msg.sender, rsETHAmount, fee, referralId, token);
    }
```
