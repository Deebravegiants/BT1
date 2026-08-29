# [H] `forceUnstakeAll` might revert due `maxStakeDebt < balance * maxLockDuration` due to rounding down.

## Summary
Severity: High
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-15
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/7
Type: hats-finding

## Details
**Github username:** @@deadrosesxyz
**Twitter username:** @deadrosesxyz
**Submission hash (on-chain):** 0xf86d5dc1bc95dd9dfcd63caf45276f27982d88359a16e88d809a787ba0b0e5c7
**Severity:** high

**Description:**
**Description**\
`forceUnstakeAll`might unexpectedly revert due to rounding down issue in `updateAccount`

**Attack Scenario**\
Let's look at the code in `forceUnstakeAll`
```solidity
    function forceUnstakeAll() external nonReentrant existingAccount {
        /// @dev Update the user's stake data
        _updateAccount(msg.sender,0);

        /// @dev Initialize cached variable
        uint256 portalEnergy = accounts[msg.sender].portalEnergy;

        /// @dev Calculate how many portalEnergyToken must be burned from the user's wallet, if any
        if(portalEnergy < accounts[msg.sender].maxStakeDebt) {

            uint256 remainingDebt = accounts[msg.sender].maxStakeDebt - portalEnergy;

            /// @dev Require that the user has enough Portal Energy Tokens
            if(IERC20(portalEnergyToken).balanceOf(address(msg.sender)) < remainingDebt) {revert InsufficientPEtokens();}
            
            /// @dev Burn the appropriate portalEnergyToken from the user's wallet to increase portalEnergy sufficiently
            _burnPortalEnergyToken(msg.sender, remainingDebt);
        }

        /// @dev Withdraw the principal from the yield source to pay the user
        uint256 balance = accounts[msg.sender].stakedBalance;
        _withdrawFromYieldSource(balance);

        /// @dev Update the user's stake info
        accounts[msg.sender].stakedBalance = 0;
        accounts[msg.sender].maxStakeDebt = 0;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/7_
