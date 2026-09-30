# [M] TitlesGraph::acknowledgeEdge() methods do

## Summary
Severity: Medium
Contest weight: 0.6914
Dataset id: 22724
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
method caches edges[edgeId_] in memory, instead of storage, which does not preserve changes to the Edge struct after the transaction concludes.
```solidity
function acknowledgeEdge(bytes32 edgeId_, bytes calldata data_)
external
override
returns (Edge memory edge)
{
if (!_isCreatorOrEntity(edges[edgeId_].to, msg.sender)) revert Unauthorized();
}
internal
returns (Edge memory edge)
{
if (!_edgeIds.contains(edgeId_)) revert NotFound();
edge = edges[edgeId_];
storage? the state isn't saved?
} else {
}
}
```
In the code snippet above, edges[edgeId_] is cached in edge, then modified.
The issue is that edge, the return variable, is marked as memory, which does not save the state after the transaction ends.
methods do not work as intended.
Add the following test to TitlesGraph.t.sol.
Run with the following command: forge test --match-test test_acknowledgeEdgeFailure -vvvv
```solidity
function test_acknowledgeEdgeFailure() public {
Node memory from = Node({
nodeType: NodeType.COLLECTION_ERC1155,
entity: Target({target: address(1), chainId: block.chainid}),
creator: Target({target: address(2), chainId: block.chainid}),
data: ""
});
Node memory to = Node({
nodeType: NodeType.TOKEN_ERC1155,
entity: Target({target: address(3), chainId: block.chainid}),
creator: Target({target: address(4), chainId: block.chainid}),
data: abi.encode(42)
});
// Only the `from` node's entity can create the edge.
vm.prank(from.entity.target);
titlesGraph.createEdge(from, to, "");
vm.expectEmit(true, true, true, true);
to.creator.target, ""
);
// Only the `to` node's creator (or the entity itself) can acknowledge it
vm.prank(to.creator.target);
titlesGraph.acknowledgeEdge(keccak256(abi.encode(from, to)), "");
(Node memory nodeTo,
Node memory nodeFrom,
bool ack,
bytes memory dataResult
) = titlesGraph.edges(titlesGraph.getEdgeId(from, to));
console.log(ack);
titlesGraph.acknowledgeEdge()
// However, the value is still false.
assert(true == ack);
}
[FAIL. Reason: panic: assertion failed (0x01)] test_acknowledgeEdgeFailure()
(gas: 429897)
Logs:
false
```

## Recommendation
The simplest fix would be to change memory to storage.
```solidity
internal
returns (Edge storage edge)
{
if (!_edgeIds.contains(edgeId_)) revert NotFound();
edge = edges[edgeId_];
} else {
}
}
```
