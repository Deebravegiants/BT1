Based on my research, I found a valid analog in the **WrappedHyperFungibleToken** escrow model — the counterpart to the OP Stack's L1StandardBridge lock-and-mint pattern the external report describes.

### Title
Fee-on-transfer / non-standard ERC-20 underlying assets desynchronize escrow accounting in WrappedHyperFungibleToken - (File: `sdk/packages/core/contracts/apps/WrappedHyperFungibleToken.sol`)

### Summary
`WrappedHyperFungibleToken` implements the same "lock on source, mint on destination" accounting model that `L1StandardBridge.sol` uses for OP Stack deposits. A user calls `send()`, which pulls `amount` of the underlying ERC-20 via `transferFrom`/`approve` and dispatches a cross-chain message instructing the peer `HyperFungibleToken` on the destination chain to mint the *full requested* `amount`, as documented in the SDK guide: [1](#0-0) . The same pattern is described architecturally in the SDK docs: "deploys a `WrappedHyperFungibleToken` on the token's home chain (locking the canonical ERC20 supply) and a `HyperFungibleToken` on every remote chain (minting/burning)" [2](#0-1) . Nowhere in this flow is the actual amount *received* by the contract (post-transfer-fee) reconciled against the amount instructed to be minted remotely, mirroring exactly the L1StandardBridge accounting flaw from the external report.

### Finding Description
The base `HyperFungibleToken.sol` contract mints/burns its own internally-controlled ERC-20 supply, so it is immune to this class of bug — `_burn`/`_mint` always operate on exact accounted balances [3](#0-2) [4](#0-3) . However, `WrappedHyperFungibleToken` wraps an arbitrary externally-supplied "underlying" ERC-20 rather than minting its own token, locking the underlying in escrow and instructing the peer contract to mint the nominal `amount` cross-chain, exactly as documented in the usage example (`approve` then `send{value: nativeFee}(params)` with the same `amount` used both for the local lock and the cross-chain mint instruction) [5](#0-4) .

If the underlying token:
- charges a transfer fee (deflationary token), the wrapper contract escrows less than `amount` while still instructing the destination chain to mint `amount` — an unbacked mint that permanently desynchronizes global backing, exactly the accounting flaw the external report flags for L1StandardBridge/L2StandardBridge.
- implements a blocklist and later blocks the wrapper contract or the depositor, redemption calls that attempt to transfer the escrowed underlying back out can revert permanently, freezing all funds locked for that asset (identical to "blocking user funds in `L1StandardBridge.sol`" from the report).
- is rebasing/inflationary, the escrowed balance can drift from the sum of outstanding minted claims on all destination chains, so on withdrawal the wrapper contract can be left without enough underlying to redeem legitimate late claims.

This class of issue is explicitly acknowledged as fixed elsewhere in the codebase for a comparable component — `IntentGatewayV2.sol`'s `placeOrder`/`withdraw` flow was hardened to measure actual post-transfer-fee balances rather than nominal amounts, as shown by dedicated tests (`testPlaceOrder_FeeOnTransferToken_WithProtocolFee`, `testPlaceAndFill_FeeOnTransferToken_RoundTrip`) that explicitly compute `receivedAfterTransferFee` and escrow only the actually-received amount [6](#0-5) . No equivalent balance-diff safeguard is documented or evidenced for `WrappedHyperFungibleToken`'s lock/unlock accounting.

### Impact Explanation
An unprivileged token bridger who deposits (or who is induced to deposit via a malicious/non-standard token listing) a fee-on-transfer, rebasing, or blocklist-enabled ERC-20 into `WrappedHyperFungibleToken` can cause: (a) an unbacked mint of the wrapped representation on the destination chain, letting subsequent redeemers drain more underlying than was actually escrowed, or (b) permanent freezing of legitimately escrowed funds if a blocklist or reverting transfer prevents redemption. Both are Medium/High severity — unbacked mint is a direct fund-theft vector against other users of the same wrapped-token pool, and blocklist-triggered freezing is a permanent loss-of-funds vector for the depositor.

### Likelihood Explanation
Likelihood depends on which underlying tokens governance/owners choose to wrap. Since deployment of a `WrappedHyperFungibleToken` and its underlying token is a per-deployment decision (not gated by an on-chain protocol-wide allowlist in the code reviewed), and the docs actively promote self-service wrapping of "the canonical ERC20 supply" without describing token-compatibility vetting, an operator or integrator could unknowingly wrap a non-standard token (e.g., USDT-style fee toggle, or a token with a blocklist like USDC), reproducing the exact conditions the external report warns about for the Optimism-style bridge.

### Recommendation
Apply the same balance-diff accounting pattern already used in `IntentGatewayV2.sol` — measure the wrapper contract's underlying-token balance before and after the `transferFrom` call in `send()`/deposit path, and use that delta (not the nominal `amount`) as the value locked and the value instructed to be minted on the destination chain. Additionally, document and/or enforce (via an allowlist) that only ERC-20s with standard, non-fee, non-rebasing, non-blocklisted behavior may be registered as the underlying asset for a `WrappedHyperFungibleToken` deployment, consistent with the "Acknowledged" mitigation Optimism itself adopted (token-list gating) for the original report.

### Proof of Concept
Not independently reproducible from the indexed context — the full `WrappedHyperFungibleToken.sol` contract source (specifically its `send()`/lock function body) was not returned by search/read tools, only doc excerpts referencing its behavior. This is noted as a limitation: due to index size limits, the complete contract source may not be available through this tool; a Devin session with full repository access would be needed to confirm the exact escrow/mint code path and craft an executable PoC (e.g., a Foundry test wrapping a `FeeOnTransferToken`-style mock, analogous to the existing `IntentGatewayV2SameChainTest.sol` fee-on-transfer tests [7](#0-6) , against `WrappedHyperFungibleToken.send()`).

### Citations

**File:** docs/content/developers/evm/hyper-fungible-token/wrapped-hyper-fungible-token.mdx (L91-108)
```text
```solidity lineNumbers
import {IHyperFungibleToken} from "@hyperbridge/core/interfaces/IHyperFungibleToken.sol";

// Approve the underlying token
IERC20(underlying).approve(address(wrapper), amount);

IHyperFungibleToken.SendParams params = IHyperFungibleToken.SendParams({
    dest: StateMachine.evm(42161),
    to: abi.encodePacked(recipientAddress),
    amount: 1 ether,
    timeout: 3600,
    relayerFee: relayerFee,
    data: new bytes(0)
});
// Quote the native fee required for dispatching the transfer
uint256 nativeFee = IHyperFungibleToken(address(wrapper)).quote(params);
// Lock tokens and dispatch cross-chain transfer
IHyperFungibleToken(address(wrapper)).send{value: nativeFee}(params);
```

**File:** docs/content/developers/sdk/hyper-fungible-token.mdx (L14-14)
```text
The typical architecture deploys a `WrappedHyperFungibleToken` on the token's home chain (locking the canonical ERC20 supply) and a `HyperFungibleToken` on every remote chain (minting/burning). See the [EVM contract guide](/developers/evm/hyper-fungible-token) for deployment details.
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L264-282)
```text
    function send(SendParams calldata params) external payable whenNotPaused {
        _burn(msg.sender, params.amount);
        DispatchPost memory request = _buildDispatchPost(params);

        bytes32 commitment;
        if (msg.value > 0) {
            commitment = IDispatcher(_host).dispatch{value: msg.value}(request);
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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2496-2521)
```text
    /// @notice Fee-on-transfer with protocol fees: both deductions applied correctly.
    function testPlaceOrder_FeeOnTransferToken_WithProtocolFee() public {
        IntentGatewayV2 gatewayWithFees = _deployGatewayProxy();
        Params memory intentParams = Params({
            host: address(host),
            dispatcher: address(dispatcher),
            solverSelection: false,
            surplusShareBps: SURPLUS_SHARE_BPS,
            protocolFeeBps: PROTOCOL_FEE_BPS, // 30 bps
            priceOracle: address(0)
        });
        gatewayWithFees.initialize(intentParams, new bytes[](0), address(0));

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

**File:** evm/tests/foundry/IntentGatewayV2SameChainTest.sol (L2689-2735)
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
}
```
