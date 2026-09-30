# [H] TSS Nodes Set Includes Slashed Node By Default

## Summary
Severity: High
Contest weight: 0.2545
Dataset id: 14401
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Slashed node can receive portion of the distributed slashing reward.
When a TSS node is slashed some of its deposit is removed and handed to the other, honest, TSS nodes. Due to an
oversight the slashed node receives some of its penalty fees back, reducing the reward that other nodes receive for
being honest.
This occurs due to an oversight in the default Golang node behaviour. Currently, the TSS Manager is responsible for
coordinating the TSS nodes signing and supplies the full TSS active node set to TSS nodes as the set of signing nodes.
This means the node being slashed is included in the set of nodes who are then rewarded from the slashing.
While it is possible for a TSS Node to generate their own set of nodes to include in the slashing message it is unlikely a
node will deviate from the default message generation behaviour as all participating signing nodes must sign the same
message in order for the message to be considered valid.

## Recommendation
Modify the TSS manager to remove the slashed node from the set of nodes broadcast to TSS nodes in the slashing
message. Alternatively the removal of the slashed node could be included in the TSS node prior to signing the message.
The slashed node could also be removed on-chain if it is found in the set of nodes that were intended to be rewarded
from the slashing. This method is more reliable however it would increase the gas costs of slashing a node.
