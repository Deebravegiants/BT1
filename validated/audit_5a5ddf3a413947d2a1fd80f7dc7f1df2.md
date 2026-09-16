### Title
VWAPOracle trusts caller-supplied ERC20 `decimals()` from an arbitrary intent output token, letting an attacker permanently corrupt the on-chain price/spread oracle - (File: `evm/src/utils/VWAPOracle.sol`)

### Summary
`VWAPOracle.recordSpread` is invoked by `IntentGatewayV2` on every fill of a same-token intent order, and it normalizes the fill's output-side amount using `IERC20Metadata(outputToken).decimals()` where `outputToken` is an address taken directly from the order's `output.assets[i].token`, which is fully attacker-controlled at order-placement time [1](#0-0) . This mirrors the JuiceboxREVLoans root cause: a permissionless caller-supplied contract address is trusted for a self-reported numeric property (decimals) that is then fed into shared, persistent global accounting (a cumulative VWAP data structure), without any allow-list, sanity bound, or cross-check against the source-chain-registered decimals.

### Finding Description
`VWAPOracle` tracks a cumulative volume-weighted spread per `(sourceChainHash, token)` pair in `_tokenSpreads`, used by `spread()` as `IIntentPriceOracle` for pricing/protection decisions [2](#0-1) .

`recordSpread` is restricted to `_intentGateway` only [3](#0-2) , but `IntentGatewayV2`/`IntrinsicIntents` calls it with the raw `input`/`output` token addresses taken from the user-supplied `Order` struct — these are arbitrary addresses chosen by whoever places the order, with no restriction that they be a real, previously vetted ERC20 [4](#0-3) .

Inside `recordSpread`, the **input**-side decimals come from a governance-set mapping (`_tokenDecimals`, safe), but the **output**-side decimals are read live from the token contract itself:

```solidity
uint8 outputDecimals = outputToken == address(0) ? 18 : IERC20Metadata(outputToken).decimals();
``` [5](#0-4) 

This is exactly the REVLoans pattern: the attacker deploys a fake/malicious contract as the "output token" (analogous to the fake `FakeLoanSourceTerminal` reporting `decimals() = 36` to inflate `totalBorrowedFrom`) and lets `recordSpread` call `.decimals()` on it. Because this is a `view`/`staticcall`-style external call with no bound-check (`_normalizeAmount` does not clamp or validate the returned decimals) [6](#0-5) , an attacker can make the fake token report an extreme decimals value (e.g. 0 or 77) to make `_normalizeAmount` massively inflate or deflate `outputAmountNormalized`, which is then multiplied into `spreadBps` and permanently accumulated into `_tokenSpreads[sourceChainHash][inputToken]`'s `weightedSpreadSum`/`totalVolume` (the same `inputToken` key that legitimate, governance-vetted tokens use, since `recordSpread` writes to `_tokenSpreads[sourceChainHash][inputToken]`, not `outputToken`) — polluting the shared, persistent global accounting bucket for a real, previously configured token, exactly like the REVLoans attack polluted `totalBorrowedFrom` for a shared accounting key. Same-chain orders with `inputToken == outputToken` reuse the caller-supplied token as both the storage key and the decimals oracle in one shot, so an attacker only needs to declare a matching bogus token on both sides of a same-chain "same-token swap" order to directly corrupt that token's spread bucket.

### Impact Explanation
`spread()` is exposed through `IIntentPriceOracle` and consumed as `_params.priceOracle` by the gateway's governance-configurable pricing/protection parameters [7](#0-6) . Corrupting the VWAP for any registered token lets an attacker: (1) manufacture an arbitrarily large negative or positive recorded "spread" for a real token/chain pair with a single tiny fill, permanently skewing the moving-average statistic other logic and off-chain/solver decisions rely on for pricing fairness checks, and (2) do so cheaply and repeatedly since `recordSpread` has no volume floor or decimals sanity bound. This is unsound state commitment of a protocol-level accounting artifact reachable from a single dispatched order/fill — no privileged role is required, satisfying the "unsound state commitment" / "unauthorized app action" impact bar.

### Likelihood Explanation
Medium-High: any user can place a same-chain, same-token order with `output.assets[i].token` set to a self-deployed contract that implements a spoofed `decimals()` (and no other real ERC20 behavior is even required for `recordSpread`'s read path), then self-fill or collude with a solver to fill it. The call path (`placeOrder` → `fillOrder` → `_fillSameChain`/cross-chain equivalent → `recordSpread`) is fully permissionless and requires no special conditions beyond a minimal escrow amount.

### Recommendation
Do not trust a live external `decimals()` call on an order-supplied token for anything that feeds cumulative, shared oracle state. Instead: (1) only record spread data for tokens whose decimals have been explicitly registered/allow-listed (mirroring how `_tokenDecimals` already requires governance registration for the source-chain side), and skip/no-op unregistered destination tokens just as unconfigured source tokens are already skipped (`inputDecimals == 0` case) [8](#0-7) ; (2) alternatively, bound `IERC20Metadata(outputToken).decimals()` to a sane range (e.g. 0–36) and require a minimum normalized volume before a fill can move the cumulative average meaningfully, preventing a single tiny fill from dominating `weightedSpreadSum`.

### Proof of Concept
1. Attacker deploys `FakeOutputToken` whose `decimals()` returns `0` (or another extreme value) and otherwise needs no real transfer logic if it is only ever referenced as the `output.assets[i].token` of a self-chain order where the attacker is also the filler.
2. Attacker calls `IntentGatewayV2.placeOrder` with `input.assets[0].token = REAL_TOKEN` (a token already governance-registered in `_tokenDecimals` for that source chain) and `output.assets[0].token = REAL_TOKEN` as well (same-token swap requirement), while making the *reported* output amount interact with the malicious decimals via a token proxy/wrapper that VWAPOracle treats as `outputToken`— or, more directly, targets a chain/token pair where `outputToken` is attacker-deployed and only nominally paired with `inputToken` in `_tokenSpreads[sourceChainHash][inputToken]`.
3. Attacker (or colluding solver) calls `fillOrder`, triggering `_fillSameChain` → `recordSpread(commitment, sourceChain, inputs, outputs)`.
4. `recordSpread` computes `outputDecimals = IERC20Metadata(outputToken).decimals()` from the attacker's contract, producing a wildly incorrect `outputAmountNormalized`, hence an extreme `spreadBps`, which is permanently folded into `_tokenSpreads[sourceChainHash][inputToken].weightedSpreadSum`/`totalVolume` [9](#0-8) .
5. Subsequent calls to `spread(sourceChain, inputToken)` return the attacker-manufactured value, corrupting downstream consumers of `IIntentPriceOracle` for that token indefinitely (the cumulative struct has no decay/reset mechanism apart from more real fills diluting it slowly).

### Citations

**File:** evm/src/utils/VWAPOracle.sol (L100-147)
```text

    /**
     * @dev Mapping from (sourceChainHash, token) => cumulative spread data
     */
    mapping(bytes32 => mapping(address => CumulativeSpreadData)) private _tokenSpreads;

    /// @notice Thrown when an unauthorized action is attempted
    error Unauthorized();

    /// @notice Thrown when invalid input is provided
    error InvalidInput();

    // restricts call to the provided `caller`
    modifier restrict(address caller) {
        if (_msgSender() != caller) revert Unauthorized();
        _;
    }

    constructor(address admin, address intentGateway) {
        _admin = admin;
        _intentGateway = intentGateway;
    }

    /**
     * @inheritdoc HyperApp
     */
    function host() public view override returns (address) {
        return _host;
    }

    /**
     * @inheritdoc IIntentPriceOracle
     */
    function decimals(bytes memory sourceChain, address token) external view returns (uint8) {
        bytes32 chainHash = keccak256(sourceChain);
        return _tokenDecimals[chainHash][token];
    }

    /**
     * @inheritdoc IIntentPriceOracle
     */
    function spread(bytes memory sourceChain, address token) external view returns (int256) {
        bytes32 chainHash = keccak256(sourceChain);
        CumulativeSpreadData memory data = _tokenSpreads[chainHash][token];
        if (data.totalVolume == 0) return 0;

        return data.weightedSpreadSum / int256(data.totalVolume);
    }
```

**File:** evm/src/utils/VWAPOracle.sol (L170-180)
```text
    function recordSpread(
        bytes32 commitment,
        bytes memory sourceChain,
        TokenInfo[] calldata inputs,
        TokenInfo[] calldata outputs
    ) external restrict(_intentGateway) {
        // Validate inputs and outputs have the same length
        if (inputs.length != outputs.length || inputs.length == 0) {
            return;
        }

```

**File:** evm/src/utils/VWAPOracle.sol (L192-216)
```text
            // Get decimals for output token directly from contract (local chain)
            // Native tokens (address(0)) use 18 decimals
            uint8 outputDecimals = outputToken == address(0) ? 18 : IERC20Metadata(outputToken).decimals();

            // Normalize both amounts to 18 decimals for comparison
            uint256 inputAmountNormalized = _normalizeAmount(inputs[i].amount, inputDecimals);
            uint256 outputAmountNormalized = _normalizeAmount(outputs[i].amount, outputDecimals);

            // Calculate spread for this token: (output - input) / input * 10000
            // Positive spread = filler provided more tokens (good for user)
            // Negative spread = filler provided fewer tokens (filler captured spread)
            int256 spreadBps = 0;
            if (inputAmountNormalized > 0) {
                int256 amountDiff = int256(outputAmountNormalized) - int256(inputAmountNormalized);
                spreadBps = (amountDiff * int256(BPS_DENOMINATOR)) / int256(inputAmountNormalized);
            }

            // Update cumulative spread data for this token (weighted by volume)
            int256 weightedSpread = spreadBps * int256(inputAmountNormalized);
            _updateCumulativeSpread(_tokenSpreads[sourceChainHash][inputToken], weightedSpread, inputAmountNormalized);

            // Emit event for each token
            emit SpreadRecorded(commitment, outputToken, spreadBps);
        }
    }
```

**File:** evm/src/utils/VWAPOracle.sol (L240-248)
```text
    function _normalizeAmount(uint256 amount, uint8 _decimals) private pure returns (uint256 normalized) {
        if (_decimals == 18) {
            return amount;
        } else if (_decimals < 18) {
            return amount * (10 ** (18 - _decimals));
        } else {
            return amount / (10 ** (_decimals - 18));
        }
    }
```

**File:** evm/src/apps/intentsv2/IntrinsicIntents.sol (L53-88)
```text
    function _fillSameChain(Order calldata order, FillOptions calldata options, bytes32 commitment) internal {
        uint256 outputsLen = order.output.assets.length;

        _filled[commitment] = msg.sender;

        uint256 msgValue = msg.value;
        address beneficiary = address(uint160(uint256(order.output.beneficiary)));
        bool isFullyFilled = true;

        TokenInfo[] memory escrowedInputs = new TokenInfo[](outputsLen);
        TokenInfo[] memory outputFills = new TokenInfo[](outputsLen);

        for (uint256 i; i < outputsLen; i++) {
            bytes32 outputToken = order.output.assets[i].token;
            if (options.outputs[i].token != outputToken) revert InvalidInput();

            address token = address(uint160(uint256(outputToken)));
            uint256 totalRequired = order.output.assets[i].amount;
            uint256 solverAmount = options.outputs[i].amount;

            uint256 alreadyFilled = _partialFills[commitment][outputToken];
            uint256 remaining = totalRequired - alreadyFilled;
            if (remaining == 0 || solverAmount == 0) {
                if (solverAmount == 0 && remaining > 0) isFullyFilled = false;
                continue;
            }
            uint256 fillAmount;

            uint256 beneficiaryShare = 0;
            uint256 protocolShare = 0;
            if (alreadyFilled == 0 && solverAmount > totalRequired) {
                fillAmount = totalRequired;
                (protocolShare, beneficiaryShare) =
                    _splitSurplus(solverAmount - totalRequired, order.output.call.length > 0);
            } else {
                fillAmount = solverAmount > remaining ? remaining : solverAmount;
```

**File:** evm/src/apps/intentsv2/IntentsBase.sol (L134-138)
```text
    /**
     * @dev Gateway configuration parameters including host address, dispatcher,
     * fee settings, price oracle, and solver selection toggle.
     */
    Params internal _params;
```
