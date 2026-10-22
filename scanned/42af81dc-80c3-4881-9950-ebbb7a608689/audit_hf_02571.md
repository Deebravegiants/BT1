# [M] The preimage DB

## Summary
Severity: Medium
Contest weight: 0.4691
Dataset id: 13868
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
[NameWrapper.sol#L520](https://github.com/code-423n4/2022-07-ens/blob/ff6e59b9415d0ead7daf31c2ed06e86d9061ae22/contracts/wrapper/NameWrapper.sol#L520)  

By design, the `NameWrapper.names` is used as a preimage DB so that the client can query the domain name by providing the token ID. The name should be correctly stored. To do so, the `NameWrapper` records the domain’s name every time it gets wrapped. And as long as all the parent nodes are recorded in the DB, wrapping a child node will be very efficient by simply querying the parent node’s name.

However, within a malicious scenario, it is possible that a subdomain can be wrapped without recording its info in the preimage DB.

Specifically, when `NameWrapper.setSubnodeOwner` / `NameWrapper.setSubnodeRecord` on a given subdomain, the following code is used to check whether the subdomain is wrapped or not. The preimage DB is only updated when the subdomain is not wrapped (to save gas I believe).
    
```solidity
function setSubnodeOwner(
    bytes32 parentNode,
    string calldata label,
    address newOwner,
    uint32 fuses,
    uint64 expiry
)
    public
    onlyTokenOwner(parentNode)
    canCallSetSubnodeOwner(parentNode, keccak256(bytes(label)))
    returns (bytes32 node)
{
    bytes32 labelhash = keccak256(bytes(label));
    node = _makeNode(parentNode, labelhash);
    (, , expiry) = _getDataAndNormaliseExpiry(parentNode, node, expiry);
    if (ens.owner(node) != address(this)) {
        ens.setSubnodeOwner(parentNode, labelhash, address(this));
        _addLabelAndWrap(parentNode, node, label, newOwner, fuses, expiry);
    } else {
        _transferAndBurnFuses(node, newOwner, fuses, expiry);
    }
}
```

However, the problem is that `ens.owner(node) != address(this)` is not sufficient to check whether the node is already wrapped. The hacker can manipulate this check by simply invoking `EnsRegistry.setSubnodeOwner` to set the owner as the `NameWrapper` contract without wrapping the node.

Consider the following attack scenario.

  * the hacker registers a 2LD domain, e.g., `base.eth`
  * he assigns a subdomain for himself, e.g., `sub1.base.eth`

    * the expiry of `sub1.base.eth` should be set as expired shortly
    * note that the expiry is for `sub1.base.eth` instead of `base.eth`, so it is safe to make it soonly expired
  * the hacker waits for expiration and unwraps his `sub1.base.eth`
  * the hacker invokes `ens.setSubnodeOwner` to set the owner of `sub2.sub1.base.eth` as NameWrapper contract
  * the hacker re-wraps his `sub1.base.eth`
  * the hacker invokes `nameWrapper.setSubnodeOwner` for `sub2.sub1.base.eth`

    * as such, `names[namehash(sub2.sub1.base.eth)]` becomes empty
  * the hacker invokes `nameWrapper.setSubnodeOwner` for `eth.sub2.sub1.base.eth`.

    * as such, `names[namehash(eth.sub2.sub1.base.eth)]` becomes `\x03eth`

It is not rated as a High issue since the forged name is not valid, i.e., without the tailed `\x00` (note that a valid name should be like `\x03eth\x00`). However, the preimage BD can still be corrupted due to this issue.

## Proof of Concept
For full details, please see [original warden submission](https://github.com/code-423n4/2022-07-ens-findings/issues/197).

## Recommendation
When wrapping node `X`, check whether `NameWrapper.names[X]` is empty directly, and update the preimage DB if it is empty.
