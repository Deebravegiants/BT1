# [H] Adversary can break deposit queue and cause

## Summary
Severity: High
Contest weight: 0.7685
Dataset id: 19907
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
Carousel.sol#L531-L538
function _mintShares(
    address to,
    uint256 id,
    uint256 amount
) internal {
    _mint(to, id, amount, EMPTY);
    _mintEmissions(to, id, amount);
}
```
When processing deposits for the deposit queue, it _mintShares to the specified receiver which makes a _mint subcall.
```solidity
ERC1155.sol#L263-L278
function _mint(address to, uint256 id, uint256 amount, bytes memory data)
    internal virtual
{
    require(to != address(0), "ERC1155: mint to the zero address");
    address operator = _msgSender();
    uint256[] memory ids = _asSingletonArray(id);
    uint256[] memory amounts = _asSingletonArray(amount);
    _beforeTokenTransfer(operator, address(0), to, ids, amounts, data);
    _balances[id][to] += amount;
    emit TransferSingle(operator, address(0), to, id, amount);
    _afterTokenTransfer(operator, address(0), to, ids, amounts, data);
    _doSafeTransferAcceptanceCheck(operator, address(0), to, id, amount, data);
}
```
The base ERC1155 _mint is used which always behaves the same way that ERC721 safeMint does, that is, it always calls _doSafeTransferAcceptanceCheck which makes a call to the receiver. A malicious user can make the receiver always revert. This breaks the deposit queue completely. Since deposits can't be canceled this WILL result in loss of funds to all users whose deposits are blocked. To make matters worse it uses first in last out so the attacker can trap all deposits before them. Users who deposited before the adversary will lose their entire deposit.

## Recommendation
Override _mint to remove the safeMint behavior so that users can't DOS the deposit queue.
