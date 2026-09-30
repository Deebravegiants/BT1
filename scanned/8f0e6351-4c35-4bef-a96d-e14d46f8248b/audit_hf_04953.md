# [M] Private vaults don't prevent non-whitelisted

## Summary
Severity: Medium
Contest weight: 0.6956
Dataset id: 22913
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The manager of a Vault can set a Vault to be public or private. When a Vault is set to be private, it should prevent unallowed users from investing but in reality, it won't accomplish that, thus defeating the whole purpose of a private Vault. In the README there's the following statement: Link to section Can set vault to be public (anyone can deposit) or private (managers chooses who can invest). When a Vault is set to be private, it should only allow whitelisted members to invest in that Vault. There's a check on the _depositFor function that ensures that only whitelisted members can call that function if the Vault is private:  
s/PoolLogic.sol#L276  
```solidity
function _depositFor(
    address _recipient,
    address _asset,
    uint256 _amount,
    uint256 _cooldown
) private onlyAllowed(_recipient) whenNotFactoryPaused whenNotPaused returns (uint256 liquidityMinted) {
```
s/PoolLogic.sol#L163-L166  
```solidity
modifier onlyAllowed(address _recipient) {
    require(_recipient == manager() || !privatePool || isMemberAllowed(_recipient), "only members allowed");
    _;
}
```
However, users can get around this limitation easily by using a whitelisted address to invest in the Vault and then transferring the shares to other non-whitelisted addresses. There's the function _beforeTokenTransfer that prevents the transfer of shares in some scenarios, but it won't prevent transferring some shares to a non-whitelisted address when the Vault is private. In conclusion, a manager setting a private Vault should be able to choose the addresses that can invest, but this won't be true because the whitelisted addresses can transfer the shares to anyone, thus defeating the whole purpose of privacy within the Vault. Even though the impact might seem to depend on speculation, this issue is breaking a restriction stated on the README, so I think it warrants medium severity language that indicates the codebase's restrictions and/or expected functionality. Issues that break these statements, irrespective of whether the impact is low/unknown, will be assigned Medium severity. High severity will be applied only if the issue falls into the High severity category in the judging guidelines.

## Recommendation
In order to mitigate this issue, it is recommended to implement on private Vaults a check to ensure that the receiver of the shares in a transfer is whitelisted:  
```solidity
function _beforeTokenTransfer(address from, address to, uint256 amount) internal virtual override {
    super._beforeTokenTransfer(from, to, amount);
    // Minting
    if (from == address(0)) {
        return;
    }
    require(!privatePool || isMemberAllowed(to));
    if (IPoolFactory(factory).receiverWhitelist(to) == true) {
        return;
    }
    require(getExitRemainingCooldown(from) == 0, "cooldown active");
}
```
