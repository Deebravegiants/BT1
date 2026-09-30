# [M] Vault Factory ownership can be changed instantly

## Summary
Severity: Medium
Contest weight: 0.2317
Dataset id: 19901
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The VaultFactoryV2 contract is supposed to use a timelock contract with a delay period when changing its owner. However, there is a loophole that allows the owner to change the owner address instantly, without waiting for the delay period to expire. This defeats the purpose of the timelock contract and exposes the VaultFactoryV2 contract to potential abuse.
In project description, timelock is required when making critical changes. Admin can only configure new markets and epochs on those markets.
2) Admin can configure new markets and epochs on those markets, Timelock can make cirital changes like changing the oracle or whitelisitng controllers.
The VaultFactoryV2 contract has a changeOwner function that is supposed to be called only by the timelock contract with a delay period.
function changeOwner(address _owner) public onlyTimeLocker {
if (_owner == address(0)) revert AddressZero();
_transferOwnership(_owner);
}
The VaultFactoryV2 contract inherits from the Openzeppelin Ownable contract, which has a transferOwnership function that allows the owner to change the owner address immediately. However, the transferOwnership function is not overridden by the changeOwner function, which creates a conflict and a vulnerability. The owner can bypass the timelock delay and use the transferOwnership function to change the owner address instantly.
function transferOwnership(address newOwner) public virtual onlyOwner {
require(newOwner != address(0), "Ownable: new owner is the zero address");
_transferOwnership(newOwner);
}
ltFactoryV2.sol#L325-L328
The transferOwnership is not worked as design (using timelock), the timelock delay become useless. This means that if the owner address is hacked or corrupted, the attacker can take over the contract immediately, leaving no time for the protocol and the users to respond or intervene.

## Recommendation
Override the transferOwnership function and add modifier onlyTimeLocker.
