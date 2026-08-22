# [M] Always-Approved Net-Zero Value Flows Can Block Normal Flow Matrix Operations

## Summary
Severity: Medium
Chain: Smart contract
Component: Circles
Published: 2024-09-19
Source: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/122
Type: hats-finding

## Details
**Github username:** @hxaro
**Twitter username:** --
**Submission hash (on-chain):** 0xbd7c26ae4f2064388b6964def5cdafd2ea51ac76d1f069281637c99568b97cb3
**Severity:** medium

**Description:**
## Description

In the operateFlowMatrix function only the net-senders of the provided streams are required to have approved the operator executing a flow matrix. First, this implies that if a flow matrix has no streams, then no vertex needs to have approved the operator for the operator to be able to touch any of the balances across the network (as described in the docs) - under the condition that the remaining constraints of `operateFlowMatrix` are satisfied, ie. net transfers are zero, and all trust relations are respected and all balances are there to be transferred. Note that it is not about requiring at least one stream, as an attacker can always add a trivial transfer as a stream, and still touch any of the balances across the graph under the constraints of the Circles protocol.

In effect the looser constraint for only checking the stream senders ([see LL552-560 of Hub.sol](https://github.com/aboutcircles/circles-contracts-v2/blob/rc-v0.3.6-alpha/src/hub/Hub.sol#L552-L560))

```js
function operateFlowMatrix() {
    ...
    // check all senders have the operator authorized
    for (uint16 i = 0; i < _streams.length; i++) {
        if (!isApprovedForAll(_flowVertices[_streams[i].sourceCoordinate], msg.sender)) {
            // Operator not approved for source.
            revert CirclesHubOperatorNotApprovedForSource(
                msg.sender, _flowVertices[_streams[i].sourceCoordinate], i, 0
            );
        }
    }
```
implies that **all Circles avatars** have "authorized all addresses as ERC1155 operators, under the additional rules of Circles _trust path fungibility_. We understand that this is the core principle of Circles, and have not seen an issue with the implementation of this in `operateFlowMatrix`. Our concern in this issue, however, relates to an attacker wanting to prevent the normal intended use of operators calling `operateFlowMatrix` to settle transfers of users.

We imagine that if attackers exist that are intent on blocking the functioning of Circles path transfers they can easily disrupt genuine path transfers, causing them to fail with high likelihood, relative to the effort for genuine operators to construct valid paths for streams and the gas-grievence these honest operators incur when their paths are invalidated by an attacker front-running their transaction with fairly generic reshufflings of the graph state. We will detail at least one such strategy for an attacker below.

## Impact

The negative impact of the liberty to reshuffle tokens at will by anyone with net-zero value transfers can be seen as two attack vectors:

1. Implementing a **race condition**:
If the trivially-approved transaction sufficiently disperses tokens, it can cause later transactions, i.e. calls to `operateFlowMatrix`, to fail, costing the users gas. Targeting central vertices, as measured for example by a high [betweenness centrality](https://en.wikipedia.org/wiki/Betweenness_centrality) value, would be an effective way of disrupting the flow of tokens through paths that are likely to be shorter. This is because vertices with high centrality are a necessary component for a large number of shortest paths between any through vertices on the graph/network. Thus this kind of attack can be done in a DDOS-like manner, disrupting the functioning of the network in an undirected manner.
In particular if an attacker wants to target a specific community, they can target to disperse maximally the tokens of the highest centrality members (vertices) by front-running the settlements of that community with such easily computed path-transfers, without needing to closely inspect the actual upcoming streams settlements, as the attacker only needs to get one condition of insufficient balance to trigger the reversal of the whole community settlement - and for their operator to restart.

2. Increasing the required path length for later transactions, thus **increasing gas costs**:

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Circles-0x6ca9ca24d78af44582951825bef9eadcb210e5cf/issues/122_
