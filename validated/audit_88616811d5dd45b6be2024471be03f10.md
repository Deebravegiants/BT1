### Title
Unilateral peer registration in `HyperFungibleToken.send()` allows user funds to be frozen and relayer fees lost when the destination has not registered the source back - (File: `sdk/packages/core/contracts/apps/HyperFungibleToken.sol`)

### Summary
`HyperFungibleToken.send()` (and its `WrappedHyperFungibleToken`/upgradeable counterparts) only checks that the *local* contract has registered the destination chain in `_supportedChains` before burning tokens and dispatching a cross-chain POST request. It never verifies that the destination contract has reciprocally registered this chain as a trusted peer. If the two sides are not mutually connected, the request is dispatched and the sender's tokens are burned, but delivery on the destination will always revert, causing the request to time out before the sender is refunded.

### Finding Description
`send()` burns the caller's tokens and builds the outbound message purely from the local `_supportedChains[params.dest]` mapping populated by the owner's `addChain` calls: [1](#0-0) [2](#0-1) 

There is no cross-chain check (e.g. a query, handshake, or connection acknowledgment) confirming that the destination contract has registered this source chain's address as its trusted peer. On the receiving side, `onAccept` independently verifies the source using its own `_supportedChains` mapping: [3](#0-2) 

If the destination has not called `addChain` for the source chain (or registered a different module ID than the actual sender address), `onAccept` reverts with `UnsupportedChain` or `UnauthorizedSource` for every relayer delivery attempt. This is structurally identical to the reported Catalyst-Exchange bug class: connection state is tracked one-sidedly (`_vaultConnection`/`_supportedChains`), and nothing enforces or verifies mutuality before a user-facing operation (`sendAsset`/`send`) is allowed to proceed.

Because the two `addChain` calls on each side are independent, uncoordinated owner transactions (normal deployment sequencing, a chain being re-deployed, or an operator forgetting/mis-typing the peer address on one side), there is a reachable window — and potentially a permanent misconfiguration — in which one contract believes it is connected to the peer while the peer does not recognize it back. Any ordinary user calling `send()` during that window is exposed, with no way to detect the missing reverse-registration off-chain since `supportedChain()` only reflects local state.

### Impact Explanation
When the destination has not registered the source:
- The user's tokens are burned immediately in `send()`.
- The ISMP POST request can never be accepted by the destination (`onAccept` always reverts), so relayers cannot deliver it.
- Tokens are only restored to the sender when the request times out and `onPostRequestTimeout` re-mints them: [4](#0-3) 
- Any `relayerFee` and dispatch fee paid by the user in `send()` is consumed servicing failed delivery attempts and the eventual timeout processing, and is not recoverable — matching the "loss of fees" impact in the analogous report.

This is a temporary freezing of user funds (until timeout) plus a permanent loss of the relayer/dispatch fee, triggered purely by calling the normal, unprivileged `send()` entry point.

### Likelihood Explanation
This does not require a malicious admin — it is a byproduct of the standard two-step deployment flow described in the project's own documentation ("Register the WrappedHFT on the home chain and any other HFT peers... On each peer chain, do the reverse — register this chain's HFT address."). Any timing gap between the two `addChain` transactions, an incomplete rollout, or an operational mistake on either side leaves a fully asymmetric, user-reachable connection. Since nothing in the contract or the ISMP dispatch path validates mutuality before allowing `send()`, this condition can occur for as long as the misconfiguration persists and affects every user who transacts against the newly (but incompletely) configured peer.

### Recommendation
Do not rely solely on unilateral local configuration for the send path. Options:
1. Require an on-chain or off-chain handshake/attestation proving the destination has registered this chain back before marking a chain as "supported" for `send()` (mirroring the reporter's suggested `otherEndIsConnected` pattern).
2. At minimum, provide a permissionless "connection status" view/function that relayers/front-ends can use to verify mutual registration before allowing users to call `send()`, and surface clear warnings/guards against dispatching to chains whose reverse registration cannot be confirmed.
3. Consider refunding/waiving fees in the `onPostRequestTimeout` path when the failure was due to `UnsupportedChain`/`UnauthorizedSource`, to limit the loss to the burn/freeze window rather than also losing relayer fees.

### Proof of Concept
1. Deploy `HyperFungibleToken` A on chain X and `HyperFungibleToken` B on chain Y.
2. Owner of A calls `A.addChain(chainY, addressB)` (A now trusts B).
3. Owner of B has not yet called (or never calls) `B.addChain(chainX, addressA)`.
4. A user calls `A.send({dest: chainY, to: recipient, amount: 100, timeout: T, relayerFee: fee, data: ""})`. `_buildDispatchPost` succeeds because `A._supportedChains[chainY]` is set, so `100` tokens are burned and the ISMP POST request with fee `fee` is dispatched: [2](#0-1) 
5. Relayers repeatedly attempt to call `B.onAccept(...)`; it reverts every time with `UnsupportedChain` because `B._supportedChains[chainX]` is empty: [3](#0-2) 
6. The user has 0 tokens on both A and B, and has already paid `fee`, until the timeout `T` elapses and someone submits a timeout proof, triggering `A.onPostRequestTimeout` to re-mint the 100 tokens back to the user — the `fee` paid is not refunded: [4](#0-3)

### Citations

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L237-256)
```text
    function _buildDispatchPost(SendParams calldata params) internal view returns (DispatchPost memory) {
        bytes memory dest = _supportedChains[params.dest];
        if (dest.length == 0) revert UnsupportedChain();

        bytes memory body = abi.encode(Message({
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

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L292-297)
```text
    function onAccept(IncomingPostRequest calldata incoming) public virtual override onlyHost whenNotPaused {
        PostRequest calldata request = incoming.request;

        bytes memory expectedSource = _supportedChains[request.source];
        if (expectedSource.length == 0) revert UnsupportedChain();
        if (keccak256(request.from) != keccak256(expectedSource)) revert UnauthorizedSource();
```

**File:** sdk/packages/core/contracts/apps/HyperFungibleToken.sol (L321-326)
```text
    function onPostRequestTimeout(PostRequestTimeout memory incoming) public virtual override onlyHost whenNotPaused {
        Message memory message = abi.decode(incoming.request.body, (Message));
        address refundee = _toAddr(message.from);
        _mint(refundee, message.amount);
        emit Refunded({to: refundee, amount: message.amount});
    }
```
