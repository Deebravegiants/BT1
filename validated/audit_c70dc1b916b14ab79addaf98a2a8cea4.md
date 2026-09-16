## Title
Wrapped bridge trusts `params.amount` instead of the actual tokens received, allowing deflationary/fee-on-transfer underlying tokens to drain escrowed reserves - (File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol)

### Summary
`WrappedHyperFungibleToken.send()` pulls the underlying ERC20 via `safeTransferFrom(msg.sender, address(this), params.amount)` and then encodes `params.amount` — the *requested* amount, not the amount actually received — into the cross-chain `Message` that is dispatched to the peer deployment. [1](#0-0)  If the underlying token has any fee-on-transfer, deflationary, or rebasing logic (the same class of quirk that fUSDT/UST exhibited on the Nerve MetaPool), the contract will escrow less than `params.amount` while promising the full `params.amount` to the destination chain.

### Finding Description
`send()` never checks the delta between the contract's underlying balance before and after `safeTransferFrom`; it just assumes `params.amount` tokens were locked: [2](#0-1) 

The `Message.amount` field built by `_buildDispatchPost` reuses the caller-supplied `params.amount` verbatim: [3](#0-2) 

On the destination/peer chain, `onAccept` unconditionally transfers `message.amount` of the underlying token to the beneficiary from that peer contract's own pool: [4](#0-3) 

Likewise, `onPostRequestTimeout` refunds the full `message.amount` back to the original sender on the source chain, even though only the post-fee amount was ever escrowed: [5](#0-4) 

This is the exact bug class from the Nerve report: the bridge assumes a 1:1 relationship between the amount a user "sends" and the amount the contract actually custodies, which breaks for tokens with transfer-time deductions (fUSDT/UST-style logic quirks). The codebase already demonstrates awareness of this exact risk elsewhere — `IntentGatewayV2` explicitly measures the balance delta around transfers to compute the true escrowed amount for fee-on-transfer tokens, e.g. `testPlaceOrder_FeeOnTransferToken_WithProtocolFee` shows the gateway records `receivedAfterTransferFee` rather than `inputAmount`: [6](#0-5)  `WrappedHyperFungibleToken` (and its upgradeable counterpart) lacks this same actual-balance-received check.

### Impact Explanation
Each cross-chain `send()` call using a deflationary/fee-on-transfer/rebasing ERC20 as the underlying token causes the contract to under-escrow relative to what it messages the destination chain to release. Over repeated calls, the destination-side reserve pool for that underlying asset is drained faster than it is topped up, permanently insolvent against legitimate unlocks/timeouts for other users — a direct fund-loss/freezing vector analogous to the 900 BNB Nerve MetaPool drain, reachable by any unprivileged user who calls `send()` with such a token configured as `_underlying`.

### Likelihood Explanation
Likelihood depends on whether an operator configures `WrappedHyperFungibleToken._underlying` to a token with transfer-time fee/deflation semantics (e.g. a fUSDT/UST-style stablecoin, or any FOT/rebasing ERC20). Given wrapped-token bridges are frequently deployed against a variety of third-party ERC20s (as evidenced by the project's own dedicated `FeeOnTransferToken` fee-on-transfer test harness used elsewhere), this is a realistic configuration and requires no privileged access to trigger — merely calling `send()`.

### Recommendation
In `WrappedHyperFungibleToken.send()` (and the upgradeable variant), measure `IERC20(_underlying).balanceOf(address(this))` before and after `safeTransferFrom`, use the actual received delta as the escrowed/dispatched `amount` in the `Message` (mirroring the pattern already used in `IntentGatewayV2`), and reject or scale-down the message accordingly so the destination side never promises more than what was truly locked.

### Proof of Concept
1. Deploy `WrappedHyperFungibleToken` configured with `_underlying` set to a fee-on-transfer token (e.g., 1% fee on transfer, as modeled by the repo's own `FeeOnTransferToken` test contract). [7](#0-6) 
2. Call `send({dest, to, amount: 1000e18, ...})`; `safeTransferFrom` moves 1000e18 tokens from caller but the contract only receives 990e18 due to the 1% fee. [8](#0-7) 
3. The dispatched `Message.amount` is still 1000e18. [9](#0-8) 
4. On the peer chain, `onAccept` releases 1000e18 of underlying to the beneficiary from the peer's shared reserve — 10e18 more than was ever escrowed on the source chain. [10](#0-9) 
5. Repeating this drains the peer contract's underlying balance below what is needed to satisfy other users' legitimate transfers/timeouts.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L234-253)
```text
    function _buildDispatchPost(HyperFungibleToken.SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(HyperFungibleToken.Message({
            from: abi.encodePacked(msg.sender),
            to: params.to,
            amount: params.amount,
            data: params.data
        }));

        return DispatchPost({
            dest: params.dest,
            to: dest,
            body: body,
            timeout: params.timeout,
            fee: params.relayerFee,
            payer: msg.sender
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-281)
```text
    function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
        uint256 msgValue = msg.value;
        if (_isWeth && msgValue >= params.amount) {
            msgValue = msgValue - params.amount;
            IWETH(_underlying).deposit{value: params.amount}();
        } else {
            IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
        }

        DispatchPost memory request = _buildDispatchPost(params);
        bytes32 commitment;
        if (msgValue > 0) {
            commitment = IDispatcher(_host).dispatch{value: msgValue}(request);
        } else {
            commitment = dispatchWithFeeToken(request);
        }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L299-336)
```text
    function onAccept(IncomingPostRequest calldata incoming) external override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        HyperFungibleToken.Message memory message = abi.decode(request.body, (HyperFungibleToken.Message));
        address beneficiary = _toAddr(message.to);

        if (_isWeth) {
            // Try a native-ETH push first (cheap for EOAs and payable contracts);
            // if the recipient cannot accept native value (no `receive()` / `fallback()
            // payable`), re-wrap the withdrawn ETH and deliver the underlying WETH as
            // an ERC-20 transfer instead. This mirrors the deposit-side flexibility of
            // `send()` (which accepts WETH from non-payable callers via `safeTransferFrom`)
            // so the refund path doesn't permanently lock funds for the same caller class.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = beneficiary.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(beneficiary, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(beneficiary, message.amount);
        }

        if (message.data.length > 0) {
            ICallDispatcher(_dispatcher).dispatch(message.data);
        }

        emit Received({
            from: message.from,
            to: beneficiary,
            source: string(request.source),
            amount: message.amount
        });
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L344-365)
```text
    function onPostRequestTimeout(PostRequestTimeout calldata incoming) external override onlyHost whenNotPaused {
        HyperFungibleToken.Message memory message = abi.decode(incoming.request.body, (HyperFungibleToken.Message));
        address refundee = _toAddr(message.from);

        if (_isWeth) {
            // Try a native-ETH push first; if the refundee cannot accept native value
            // (e.g. the caller used the ERC-20 deposit path in `send()` from a
            // non-payable contract), re-wrap the withdrawn ETH and deliver the
            // underlying WETH as an ERC-20 transfer so the timeout still settles and
            // funds are not permanently locked.
            IWETH(_underlying).withdraw(message.amount);
            (bool sent,) = refundee.call{value: message.amount}("");
            if (!sent) {
                IWETH(_underlying).deposit{value: message.amount}();
                IERC20(_underlying).safeTransfer(refundee, message.amount);
            }
        } else {
            IERC20(_underlying).safeTransfer(refundee, message.amount);
        }

        emit Refunded({to: refundee, amount: message.amount});
    }
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2509-2521)
```text
        FeeOnTransferToken fot = new FeeOnTransferToken(100); // 1% transfer fee
        fot.mint(user, 10000 * 1e18);

        uint256 inputAmount = 1000 * 1e18;
        uint256 receivedAfterTransferFee = inputAmount - (inputAmount * 100) / 10000; // 990
        uint256 protocolFee = (receivedAfterTransferFee * PROTOCOL_FEE_BPS) / 10000;
        uint256 expectedEscrow = receivedAfterTransferFee - protocolFee;

        TokenInfo[] memory inputs = new TokenInfo[](1);
        inputs[0] = TokenInfo({token: bytes32(uint256(uint160(address(fot)))), amount: inputAmount});

        TokenInfo[] memory outputAssets = new TokenInfo[](1);
        outputAssets[0] = TokenInfo({token: bytes32(uint256(uint160(address(dai)))), amount: 900 * 1e18});
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2690-2735)
```text
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
}
```
