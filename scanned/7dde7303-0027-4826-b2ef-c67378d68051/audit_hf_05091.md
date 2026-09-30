# [M] The circulating_supply() of the Minter contract may revert, causing the Minter to fail to periodically emit Flow tokens, leading to systemic DOS risks.

## Summary
Severity: Medium
Contest weight: 0.6889
Dataset id: 23112
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The circulating_supply() of the Minter contract may revert, causing the Minter to fail to periodically emit Flow tokens, leading to systemic DOS risks. The code for the Minter contract to emit Flow tokens weekly is in the update_period() function:
```solidity
function update_period() external returns (uint) {
    uint _period = active_period;
    if (block.timestamp >= _period + WEEK && initializer == address(0)) { // only trigger if new week
        _period = (block.timestamp / WEEK) * WEEK;
        active_period = _period;
        uint256 weekly = weekly_emission();
        uint _required = _flow.totalSupply() - _ve.totalSupply();
        uint _balanceOf = _flow.balanceOf(address(this));
        if (_balanceOf < _required) {
            _flow.mint(address(this), _required - _balanceOf);
        }
        _checkpointRewardsDistributors();
        _flow.approve(address(_voter), weekly);
        _voter.notifyRewardAmount(weekly);
        emit Mint(msg.sender, weekly, circulating_supply());
    }
    return _period;
}
```
Please pay attention to this statement of the update_period function:
```solidity
emit Mint(msg.sender, weekly, circulating_supply());
```
If the value of _flow.totalSupply() is less than the value of _ve.totalSupply() in the circulating_supply() function, a revert will occur, preventing the normal emission of flow tokens during the update_period. This situation is possible. When the flow-weth pool has good liquidity and the price of flow token is relatively high, the minting amount of lpToken may exceed the total supply of flow token. When there are enough lpToken staked to veEscrow contract, _ve.totalSupply() will be greater than _flow.totalSupply(), which is a potential systemic DOS risk that may occur. The circulating_supply() of the Minter contract may revert, resulting in the inability of the Minter to periodically emit Flow tokens, posing a systemic DOS risk.

## Recommendation
```solidity
function circulating_supply() public view returns (uint) {
    return _flow.totalSupply() > _ve.totalSupply() ? _flow.totalSupply() - _ve.totalSupply() : 0;
}
```
