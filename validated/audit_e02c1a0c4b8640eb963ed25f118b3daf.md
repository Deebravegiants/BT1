### Title
HyperbridgeLzEndpoint's cross-chain source check relies on deterministic CREATE2 address reuse, letting a front-runner hijack the "same address" trust assumption and forge/redirect messages - (File: sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol)

### Summary
`HyperbridgeLzEndpoint` authenticates incoming ISMP deliveries purely by checking `request.from == address(this)`, relying on the assumption that the contract occupies the *same address* on every chain and is therefore controlled by the *same trusted deployer* everywhere. This is exactly the deployment-address trust assumption flagged in the LifeBuoy report: when the address is derived via CREATE2 from a salt/bytecode that anyone can supply to a shared or permissionless factory (which is precisely how the docs instruct users to deploy it — `new HyperbridgeLzEndpoint{salt: salt}(admin)` with no further access control on who calls that constructor), an attacker can race the legitimate owner to occupy that address on a chain the owner has not yet deployed to, or use a different deployment path that reproduces the same address with attacker-controlled `owner`.

### Finding Description
The adapter's own documentation states the security model explicitly: [1](#0-0) . The tests confirm the mechanism operationally — `onAccept` accepts a delivery only when `request.from` equals the local contract's own encoded address, and rejects any other source with `UnknownSource`: [2](#0-1) , and a matching-address `from` field is required for a delivery to be treated as legitimate: [3](#0-2) .

The contract's own NatSpec documents that it "Assumes the same contract address on all chains (CREATE2 deployment)": [4](#0-3) . Deployment guidance recommends CREATE2 with a fixed salt and states the constructor should ideally take no args "for CREATE2 compatibility": [5](#0-4) , while other snippets show the constructor still takes an `admin`/`owner` parameter: [6](#0-5) .

Exactly as in the LifeBuoy analog, this address-equality check does not verify *who deployed* the contract at that address — it only verifies that the code at that slot self-identifies with a matching address. If the endpoint (or any factory it is deployed through) is not deployed strictly from a single EOA via plain `CREATE`, or is deployed via a shared/permissionless CREATE2 factory using a publicly known salt (as instructed in the docs/scripts, e.g. `bytes32 salt = keccak256("hyperbridge-lz-v1")`), any third party can:
1. Precompute the same deterministic address on a chain the legitimate operator has not yet deployed to, and deploy their own `HyperbridgeLzEndpoint` there first, becoming `owner` and controlling `setEidMapping`, `setRelayerFee`, `pause`, etc.
2. Once an OApp/OFT operator (unaware of the front-run) registers this address as a trusted peer via `setPeer(dstEid, address)` — trusting that the same CREATE2 address implies the same legitimate operator — the attacker's contract now sits at the position the source-verification model implicitly trusts, and can configure eid mappings and forward attacker-chosen ISMP-relayed payloads through `onAccept`/`lzReceive` to the victim OApp as if they came from the legitimate peer.

This mirrors the LifeBuoy finding's core defect: "the only reliably safe way to deploy this contract... would be to either deploy via `create` directly from an EOA, or to deploy via `create2` from an authorization-protected factory" — a constraint that is neither enforced nor documented here beyond a documentation note that "the adapter assumes the same contract address on all chains."

### Impact Explanation
If an attacker wins the address race (or replicates the deployment via a shared factory) before the legitimate deployer/operator finishes rolling out the endpoint to all intended chains, they gain owner control of the "trusted" endpoint identity on that chain. Since `onAccept`'s only authentication of the counterparty is address equality with itself, and OApps register peers by address under the assumption that identical CREATE2 addresses across chains imply a single trusted operator, the attacker can manipulate `setEidMapping` to redirect or accept forged state-machine sources, and ultimately relay attacker-controlled `lzReceive` calls to victim OFTs/OApps that trust this endpoint — resulting in forged message delivery and potential theft of bridged token balances routed through the compromised chain's endpoint.

### Likelihood Explanation
Exploitation requires only a public deployment race or use of a shared CREATE2 factory with a known salt (both of which the documentation itself recommends), and does not require any privileged access — any actor watching for endpoint deployments across supported EVM chains can front-run an as-yet-undeployed chain. This is directly analogous to the "attacker can have a script running to monitor... and immediately deploy" scenario in the original report.

### Recommendation
Either remove/soften the reliance on "same CREATE2 address implies same trusted operator" as the sole authentication mechanism, or explicitly document and enforce (e.g., via an authorization-gated factory, or deployment strictly from a single fixed EOA via `CREATE`) the specific deployment pattern required for the cross-chain address-equality assumption to hold. Consider augmenting `onAccept`'s source check with an explicit, owner-configured peer registry (as `BridgeToken`/`HyperFungibleToken` already do via `_supportedChains`/`addChain`) rather than relying purely on `request.from == address(this)`.

### Proof of Concept
1. Operator publishes the intended deployment salt/bytecode for `HyperbridgeLzEndpoint` (as recommended in the docs) intending to deploy identically on Ethereum and Arbitrum via CREATE2 with `salt = keccak256("hyperbridge-lz-v1")`.
2. Operator deploys on Ethereum first; an attacker monitoring pending deployments computes the same CREATE2 address for Arbitrum and deploys their own `HyperbridgeLzEndpoint{salt: salt}(attackerOwner)` on Arbitrum first, since deployment is permissionless (see [6](#0-5) , `admin` is any caller-supplied argument).
3. Downstream OApps/OFTs configure `setPeer(arbitrumEid, thatAddress)` trusting the deterministic-address assumption. The attacker, as owner, configures `setEidMapping` and can drive `onAccept` deliveries (as validated purely by `request.from == address(this)` per [2](#0-1) ) to forge or manipulate messages delivered to the victim OApp's `lzReceive`.

Note: I was unable to view the full `onAccept` function body (only excerpts and tests) within the available indexed context; the exact revert conditions beyond the `UnknownSource`/`InvalidNonce` checks observed in tests could not be fully confirmed. For complete verification of `onAccept`'s full logic, a Devin session with full repository access would be needed.

### Citations

**File:** docs/content/developers/evm/lz-endpoint.mdx (L45-45)
```text
The adapter assumes the same contract address on all chains via CREATE2 deployment. It verifies incoming messages by checking that `request.from` matches its own address — if it's the same contract on both chains, only legitimate messages from the adapter on the source chain are accepted.
```

**File:** docs/content/developers/evm/lz-endpoint.mdx (L63-68)
```text
```solidity lineNumbers
import {HyperbridgeLzEndpoint} from "@hyperbridge/lz-endpoint/HyperbridgeLzEndpoint.sol";

bytes32 salt = keccak256("hyperbridge-lz-v1");
HyperbridgeLzEndpoint endpoint = new HyperbridgeLzEndpoint{salt: salt}(admin);
```
```

**File:** sdk/packages/lz-endpoint/test/HyperbridgeLzEndpointTest.sol (L226-234)
```text
        PostRequest memory request = PostRequest({
            source: srcStateMachine,
            dest: dstStateMachine,
            nonce: 0,
            from: abi.encodePacked(address(dstEndpoint)),
            to: abi.encodePacked(address(dstEndpoint)),
            timeoutTimestamp: 0,
            body: body
        });
```

**File:** sdk/packages/lz-endpoint/test/HyperbridgeLzEndpointTest.sol (L315-331)
```text
    function testRejectUnknownSource() public {
        bytes memory body = abi.encode(bytes32(0), SRC_EID, bytes32(0), uint64(1), bytes32(0), "");

        PostRequest memory request = PostRequest({
            source: srcStateMachine,
            dest: dstStateMachine,
            nonce: 0,
            from: abi.encodePacked(address(0xDEAD)), // wrong source
            to: abi.encodePacked(address(dstEndpoint)),
            timeoutTimestamp: 0,
            body: body
        });

        vm.prank(MAINNET_HOST);
        vm.expectRevert(HyperbridgeLzEndpoint.UnknownSource.selector);
        dstEndpoint.onAccept(IncomingPostRequest({request: request, relayer: address(0)}));
    }
```

**File:** sdk/packages/lz-endpoint/contracts/HyperbridgeLzEndpoint.sol (L39-50)
```text
/**
 * @title HyperbridgeLzEndpoint
 * @author Polytope Labs (hello@polytope.technology)
 * @notice A LayerZero V2 endpoint adapter that routes messages through Hyperbridge's ISMP
 * protocol. Existing OFTs can point to this contract as their LayerZero endpoint to use
 * Hyperbridge for cross-chain transport without code changes.
 *
 * @dev Implements `ILayerZeroEndpointV2` for OApp compatibility and `HyperApp` for ISMP
 * message handling. Assumes the same contract address on all chains (CREATE2 deployment).
 *
 * EID-to-StateMachine mapping is owner-configured via `setEidMapping()`.
 */
```

**File:** sdk/packages/lz-endpoint/README.md (L66-82)
```markdown
## Deployment

```solidity
// Deploy the adapter (no constructor args for CREATE2 compatibility)
HyperbridgeLzEndpoint endpoint = new HyperbridgeLzEndpoint();

// Configure host and local eid
endpoint.setHost(ismpHostAddress, localEid);

// Register chain mappings (LZ eid <-> ISMP state machine ID)
endpoint.setEidMapping(30101, StateMachine.evm(1));       // Ethereum
endpoint.setEidMapping(30110, StateMachine.evm(42161));    // Arbitrum
endpoint.setEidMapping(30111, StateMachine.evm(10));       // Optimism

// Deploy a new OApp pointing to this adapter
MyOFT oft = new MyOFT(address(endpoint), delegate);
```
```
