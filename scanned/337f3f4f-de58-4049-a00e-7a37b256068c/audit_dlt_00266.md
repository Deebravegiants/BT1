# [H] CL-2023-01: The lighthouse beacon nodes can be crashed via malicious BlocksByRange messages containing an overly large 'count' value

## Summary
Severity: High
Chain: Ethereum (consensus layer)
Component: Lighthouse
Published: 2023-05-03
Source: https://notes.ethereum.org/mw-M7HxuRM-09nSPVqp52A
Type: ef-disclosure

## Details
# The lighthouse beacon nodes can be crashed via malicious BlocksByRange messages containing an overly large 'count' value

## Short description
### 1 sentence description of the bug
The lighthouse beacon nodes can be crashed via malicious BlocksByRange messages containing an overly large 'count' value
## Attack scenario
### More detailed description of the attack/bug scenario and unexpected/buggy behaviour
(I apologise in advance for any formatting ugliness in this report. I wasn't too sure in what format you'd receive this, hence I'm unsure as to how I should apply formatting here. I've used markdown for code snippets)

Attackers are able to crash lighthouse nodes by sending malicious BlocksByRange messages. For reference, the relevant message structs are as follows:

(beacon_node/lighthouse_network/src/rpc/methods.rs)

```
/// Request a number of beacon block roots from a peer.
#[derive(Encode, Decode, Clone, Debug, PartialEq)]
pub struct BlocksByRangeRequest {
    /// The starting slot to request blocks.
    pub start_slot: u64,

    /// The number of blocks from the start slot.
    pub count: u64,
}

/// Request a number of beacon block roots from a peer.
#[derive(Encode, Decode, Clone, Debug, PartialEq)]
pub struct OldBlocksByRangeRequest {
    /// The starting slot to request blocks.
    pub start_slot: u64,

    /// The number of blocks from the start slot.
    pub count: u64,

    /// The step increment to receive blocks.
    ///
    /// A value of 1 returns every block.
    /// A value of 2 returns every second block.
    /// A value of 3 returns every third block and so on.
```

_Trimmed to 38 lines — full report: https://notes.ethereum.org/mw-M7HxuRM-09nSPVqp52A_
