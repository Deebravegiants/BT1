### Title
Tron `IntentGatewayV2.placeOrder` credits escrow using nominal amounts instead of actual received amounts, breaking accounting for fee-on-transfer/deflationary tokens - (File: `evm/tron/contracts/apps/IntentGatewayV2.sol`)

### Summary
The Tron variant of `IntentGatewayV2.sol` does not implement the fee-on-transfer safeguard that exists in the main EVM `IntentGatewayV2.sol`. It credits the internal escrow ledger `_orders[commitment][token]` with the user-specified/reduced input amount rather than the actual amount of tokens received by the contract, letting deflationary or fee-on-transfer ERC20 tokens desynchronize escrow accounting from real token balances.

### Finding Description
In the reachable EVM `IntentGatewayV2.sol` (`evm/src/apps/IntentGatewayV2.sol`), `placeOrder` explicitly protects against fee-on-transfer tokens by measuring balance before/after each `safeTransferFrom` and mutating `order.inputs[i].amount` to the actual received amount before it is used to compute the commitment and to credit escrow: [1](#0-0) 

The Tron port (`evm/tron/contracts/apps/IntentGatewayV2.sol`), which shares the exact same `Order`/escrow model and is reachable by the same untrusted `placeOrder(order, graffiti)` entrypoint, omits this check entirely. In the direct-transfer path it calls `safeTransferFrom` for the nominal `order.inputs[i].amount` and then unconditionally credits escrow with the (only protocol-fee-)reduced nominal amount, never checking the gateway's actual token balance delta: [2](#0-1) 

The predispatch path has the same flaw: dust is computed relative to `requiredAmount` (the nominal amount), but the amount credited to escrow (`_orders[commitment][token] += reducedInputs[i].amount`) is still derived from the nominal input amount rather than the token balance actually swept back to the gateway: [3](#0-2) 

If `token` charges a transfer fee (fee-on-transfer/deflationary/rebasing), the gateway's real `IERC20(token).balanceOf(address(this))` increase will be less than `reducedInputs[i].amount`, yet `_orders[commitment][token]` is credited as if the full nominal amount arrived. This is the exact bug class described in the Rubicon/RubiconMarket report: `info.pay_amt` (here, `_orders[commitment][token]`) is set from the requested amount instead of the balance-diff-derived actual amount.

### Impact Explanation
Because `withdraw()` (called from `onAccept` for `RedeemEscrow`/`RefundEscrow`, or directly for same-chain cancel) pays out `body.tokens[i].amount` against the `_orders[commitment][token]` ledger without re-verifying the gateway's live token balance, an inflated escrow record for one order (using a fee-on-transfer token) causes the contract's internal accounting to exceed its true token holdings. This is a real solvency break: subsequent legitimate withdrawals/refunds for other orders denominated in the same token can fail or be partially satisfied because the token balance was already deficient, or an attacker can place many small fee-on-transfer-token orders and immediately cancel (same-chain path calls `withdraw` synchronously) to repeatedly extract more tokens from the pooled contract balance than they deposited, draining tokens escrowed by other users of the same token. This meets the "concrete theft or permanent freezing of funds" bar via broken order-book/escrow accounting reachable from a single unprivileged `placeOrder` call.

### Likelihood Explanation
Likelihood is Medium: the IntentGateway is permissionless with respect to which ERC20 token can be used as `order.inputs[i].token` — there is no token whitelist visible in this contract, and any attacker can deploy or use an existing fee-on-transfer/deflationary token as an input asset. No special privilege is required — `placeOrder` is a normal user-facing entrypoint, and the same-chain `cancelOrder`→`withdraw` flow is immediately reachable within the same or a following transaction, making exploitation straightforward for any user willing to use such a token.

### Recommendation
Apply the same balance-diff protection used in `evm/src/apps/IntentGatewayV2.sol` to the Tron contract: for every ERC20 leg (both the direct-transfer branch and the predispatch/dispatcher-sweep branch), record `balanceOf(address(this))` before the transfer/sweep and after, and use the delta (not the nominal `order.inputs[i].amount`/`reducedInputs[i].amount`) both for the commitment hash and for crediting `_orders[commitment][token]`. Alternatively, adopt a token whitelist to reject fee-on-transfer/deflationary tokens if consistent balance-diff accounting cannot be guaranteed across all code paths (predispatch, direct transfer, fee escrow).

### Proof of Concept
1. Deploy a fee-on-transfer ERC20 `FOT` that burns/keeps 10% of every transfer (as in the existing test helper `FeeOnTransferToken` used against the main gateway: [4](#0-3) ).
2. On the Tron gateway, call `placeOrder` with `order.inputs[0] = {token: FOT, amount: 1000e18}`, same-chain source/destination, `protocolFeeBps = 0`.
3. Because of `IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount)` at `evm/tron/contracts/apps/IntentGatewayV2.sol:459`, the gateway actually receives only 900 FOT, but `_orders[commitment][token] += reducedInputs[i].amount` at line 463 credits 1000 FOT to escrow.
4. Immediately call `cancelOrder` on the same chain; `withdraw()` is invoked internally and transfers `body.tokens[i].amount = 1000e18` FOT out of the gateway — but the FOT transfer itself burns another 10%, and more importantly the ledger already assumed 1000 FOT were escrowed while only 900 were ever held, meaning the deficit is drawn from other users' escrowed FOT balances in the same contract, corrupting the order book / draining funds belonging to other order placers using the same token.

### Citations

**File:** evm/src/apps/IntentGatewayV2.sol (L313-323)
```text
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    uint256 balBefore = IERC20(token).balanceOf(address(this));
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                    order.inputs[i].amount = IERC20(token).balanceOf(address(this)) - balBefore;
                }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L416-446)
```text
            // Transfer tokens from call dispatcher back to IntentGateway
            Call[] memory transferCalls = new Call[](inputsLen);
            for (uint256 i; i < inputsLen;) {
                address token = address(uint160(uint256(order.inputs[i].token)));
                uint256 requiredAmount = order.inputs[i].amount;
                uint256 balance;

                if (token == address(0)) {
                    balance = address(dispatcher).balance;
                    if (balance < requiredAmount) revert InsufficientNativeToken();
                    transferCalls[i] = Call({to: address(this), value: balance, data: ""});
                } else {
                    balance = IERC20(token).balanceOf(dispatcher);
                    if (balance < requiredAmount) revert InvalidInput();
                    transferCalls[i] = Call({
                        to: token,
                        value: 0,
                        data: abi.encodeWithSelector(IERC20.transfer.selector, address(this), balance)
                    });
                }

                uint256 dust = balance - requiredAmount;
                if (dust > 0) emit DustCollected(token, dust);

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
```

**File:** evm/tron/contracts/apps/IntentGatewayV2.sol (L450-469)
```text
        } else {
            for (uint256 i; i < inputsLen;) {
                if (order.inputs[i].amount == 0) revert InvalidInput();
                address token = address(uint160(uint256(order.inputs[i].token)));
                if (token == address(0)) {
                    // native token
                    if (msgValue < order.inputs[i].amount) revert InsufficientNativeToken();
                    msgValue -= order.inputs[i].amount;
                } else {
                    IERC20(token).safeTransferFrom(msg.sender, address(this), order.inputs[i].amount);
                }

                // Store reduced amount (after protocol fees) in escrow
                _orders[commitment][token] += reducedInputs[i].amount;

                unchecked {
                    ++i;
                }
            }
        }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2689-2734)
```text
/// @dev ERC20 with a configurable transfer fee (in basis points).
contract FeeOnTransferToken {
    string public name = "FeeOnTransferToken";
    string public symbol = "FOT";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    uint256 public feeBps;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor(uint256 _feeBps) {
        feeBps = _feeBps;
    }

    function mint(address to, uint256 amount) external {
        balanceOf[to] += amount;
        totalSupply += amount;
    }

    function approve(address spender, uint256 amount) external returns (bool) {
        allowance[msg.sender][spender] = amount;
        return true;
    }

    function transfer(address to, uint256 amount) external returns (bool) {
        return _transfer(msg.sender, to, amount);
    }

    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        uint256 allowed = allowance[from][msg.sender];
        if (allowed != type(uint256).max) {
            allowance[from][msg.sender] = allowed - amount;
        }
        return _transfer(from, to, amount);
    }

    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        uint256 fee = (amount * feeBps) / 10_000;
        uint256 received = amount - fee;
        balanceOf[from] -= amount;
        balanceOf[to] += received;
        // fee is burned
        totalSupply -= fee;
        return true;
    }
```
