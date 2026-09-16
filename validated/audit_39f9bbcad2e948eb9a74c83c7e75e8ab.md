### Title
`WrappedHyperFungibleToken.send()` dispatches the requested amount instead of the actual tokens received, allowing fee-on-transfer or deflationary ERC20s to mint unbacked supply on remote chains - ([File: sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol])

### Summary
`WrappedHyperFungibleToken.send()` pulls `params.amount` from the caller via `safeTransferFrom` but never checks how much the contract actually received before encoding `message.amount = params.amount` into the cross-chain dispatch. [1](#0-0)  For any underlying ERC20 that doesn't transfer the full nominal amount (fee-on-transfer, rebasing, deflationary tokens), the contract locks less than `params.amount` but instructs the peer `HyperFungibleToken` on the destination chain to mint the full, unreduced `params.amount`. [2](#0-1) 

### Finding Description
This is the same bug class as the THORChain July 2021 incident: the protocol trusted a caller-supplied/expected transfer amount instead of measuring the actual balance delta, letting an attacker credit more value cross-chain than was actually deposited.

In `WrappedHyperFungibleToken.send()`:
```solidity
function send(HyperFungibleToken.SendParams calldata params) external payable whenNotPaused {
    uint256 msgValue = msg.value;
    if (_isWeth && msgValue >= params.amount) {
        ...
    } else {
        IERC20(_underlying).safeTransferFrom(msg.sender, address(this), params.amount);
    }
    DispatchPost memory request = _buildDispatchPost(params);   // encodes params.amount, not actual received
    ...
}
``` [1](#0-0) 

`_buildDispatchPost` encodes `message.amount = params.amount` verbatim: [3](#0-2) 

On the destination chain, `HyperFungibleToken.onAccept` mints exactly `message.amount` to the beneficiary with no reference to what was actually locked on the source: [4](#0-3) 

The codebase demonstrates the team is aware of this exact bug class and has already fixed it elsewhere: `IntentGatewayV2.placeOrder` explicitly snapshots balances before/after transfer and mutates `order.inputs[i].amount` to the *actual received* amount before computing the commitment/escrow, with a comment: "For fee-on-transfer tokens, the gateway receives less than the requested amount. We mutate order.inputs to reflect actual received so the commitment and escrow are consistent with what the gateway holds." [5](#0-4)  A foundry test even validates this behavior for `IntentGatewayV2` with a `FeeOnTransferToken`. [6](#0-5)  `WrappedHyperFungibleToken.send()` and its upgradeable twin `WrappedHyperFungibleTokenUpgradeable.send()` lack this same balance-delta accounting. [7](#0-6) 

### Impact Explanation
Any deployment of `WrappedHyperFungibleToken`/`WrappedHyperFungibleTokenUpgradeable` wrapping a fee-on-transfer, deflationary, or rebasing ERC20 will systematically mint more tokens on remote `HyperFungibleToken` deployments than is actually escrowed in the wrapper. Each `send()` call widens the gap between locked collateral and minted remote supply. Over repeated sends, remote-chain holders redeeming back through the wrapper (`onAccept`/unlock path) will eventually be unable to be paid out because the wrapper's actual token balance is less than the aggregate amount promised across all mints — a permanent insolvency/fund-freezing condition for later redeemers, and an unbacked-mint condition on the remote chain. This is a Medium/High severity logic bug reachable by any unprivileged user who calls `send()` with a fee-on-transfer token configured as `_underlying` — no special privileges required, matching the "logic vulnerability" and "unbacked mint" criteria from the rules.

### Likelihood Explanation
Deployment configuration determines exploitability: the wrapper is designed to wrap "existing ERC20 tokens" generically (docs explicitly market it for arbitrary ERC20s, e.g., USDC), and nothing in `configure()` restricts `_underlying` to conventional, non-fee tokens. [8](#0-7)  Given how common fee-on-transfer and deflationary tokens are in the wild, any governance/owner selecting such a token for wrapping (or a user tricking an owner into it, or a token later adding a transfer fee via an upgradeable proxy) would trigger this continuously and cumulatively, not as a one-off edge case.

### Recommendation
Mirror the fix already applied in `IntentGatewayV2.placeOrder`: measure `_underlying`'s balance of `address(this)` before and after `safeTransferFrom`, and use the actual received delta as `message.amount` in `_buildDispatchPost`, instead of trusting `params.amount`. Apply the same fix to `WrappedHyperFungibleTokenUpgradeable.send()`.

### Proof of Concept
1. Owner deploys `WrappedHyperFungibleToken`, configures `_underlying` to a fee-on-transfer ERC20 (e.g., 1% fee), and registers a peer `HyperFungibleToken` on chain B.
2. User calls `send({amount: 1000, to: attacker, dest: chainB, ...})`. `safeTransferFrom` moves only 990 tokens into the wrapper (10 taken as fee), but `_buildDispatchPost` still encodes `message.amount = 1000`. [9](#0-8) 
3. On chain B, `HyperFungibleToken.onAccept` mints 1000 tokens to `attacker`, even though only 990 are actually held in escrow on chain A. [10](#0-9) 
4. Attacker repeats this send/redeem cycle (bridge back and forth) to compound the wrapper's shortfall, or simply waits for the wrapper to become insolvent as multiple users bridge the fee-on-transfer token, then races to redeem before the wrapper depletes — later redeemers cannot unlock underlying tokens because `IERC20(_underlying).safeTransfer(beneficiary, message.amount)` in `onAccept`/timeout paths will revert or leave the wrapper's balance insufficient. [11](#0-10) 

**Note on tool limitations:** I could not execute a live Foundry PoC (read-only ask mode); the above trace is based on static code review of the cited functions. If test coverage for `WrappedHyperFungibleToken` with fee-on-transfer tokens exists in the repo, I did not find it — the only fee-on-transfer test coverage located was for `IntentGatewayV2`, which strongly suggests this specific contract path lacks equivalent protection/tests.

### Citations

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L178-185)
```text
    function configure(WrappedConfigOptions calldata options) external onlyOwner {
        if (_host == address(0)) {
            _host = options.host;
        }
        _dispatcher = options.dispatcher;
        _underlying = options.underlying;
        _isWeth = options.isWeth;
    }
```

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

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol (L266-290)
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

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-313)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();

        Message memory message = abi.decode(request.body, (Message));
        address beneficiary = _toAddr(message.to);
        _mint(beneficiary, message.amount);

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

**File:** evm/src/apps/IntentGatewayV2.sol (L228-234)
```text
        uint256 inputsLen = order.inputs.length;

        // Phase 1: Transfer tokens and record actual received amounts.
        // For fee-on-transfer tokens, the gateway receives less than the requested amount.
        // We mutate order.inputs to reflect actual received so the commitment and escrow
        // are consistent with what the gateway holds.
        uint256 msgValue = msg.value;
```

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2461-2494)
```text
            destination: host.host(),
            deadline: block.number + 100,
            nonce: 0,
            fees: 0,
            session: address(0),
            predispatch: DispatchInfo({assets: new TokenInfo[](0), call: ""}),
            inputs: inputs,
            output: output
        });

        vm.startPrank(user);
        fot.approve(address(intentGateway), inputAmount);
        intentGateway.placeOrder(order, bytes32(0));
        vm.stopPrank();

        // Gateway should hold only what it actually received
        assertEq(
            fot.balanceOf(address(intentGateway)), expectedReceived, "Gateway balance should match received amount"
        );

        // Reconstruct the order as placeOrder would have mutated it
        order.user = bytes32(uint256(uint160(user)));
        order.source = host.host();
        order.nonce = 0;
        order.inputs[0].amount = expectedReceived;
        bytes32 commitment = keccak256(abi.encode(order));

        // Escrow should match actual received, not the user-specified amount
        assertEq(
            intentGateway._orders(commitment, address(fot)),
            expectedReceived,
            "Escrow should equal actual received amount"
        );
    }
```

**File:** sdk/packages/core/contracts/apps/WrappedHyperFungibleTokenUpgradeable.sol (L294-318)
```text
    function send(HyperFungibleTokenUpgradeable.SendParams calldata params) external payable whenNotPaused {
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

        emit Sent({
            from: msg.sender,
            to: params.to,
            dest: string(params.dest),
            amount: params.amount,
            commitment: commitment
        });
    }
```
