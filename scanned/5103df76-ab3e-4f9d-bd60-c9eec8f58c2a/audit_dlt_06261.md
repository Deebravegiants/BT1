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
        portalEnergy = accounts[msg.sender].portalEnergy -= (balance * maxLockDuration) / SECONDS_PER_YEAR;
        accounts[msg.sender].availableToWithdraw = 0;

        /// @dev Send the user´s staked balance to the user
        IERC20(PRINCIPAL_TOKEN_ADDRESS).safeTransfer(msg.sender, balance);
        
        /// @dev Update the global tracker of staked principal
        totalPrincipalStaked -= balance;

        /// @dev Emit an event with the updated stake information
        emit StakePositionUpdated(msg.sender, 
        block.timestamp,
        maxLockDuration,
        0,
        0, 
        portalEnergy,
        0);
    }
```
The `if` check is the important part we're looking at: 
```solidity
if(portalEnergy < accounts[msg.sender].maxStakeDebt) {
```

If the user doesn't have enough portalEnergy, they burn some of their tokens in order for the `portalEnergy == maxStakeDebt`


This makes the assumption that `maxStakeDebt` should never be < `balance * maxLockDuration`, (as we later  have the following line:)
```solidity
portalEnergy = accounts[msg.sender].portalEnergy -= (balance * maxLockDuration) / SECONDS_PER_YEAR;
```

However due to rounding down issues we can get to a state where `maxStakeDebt < balance * maxLockDuration` and this line underflows 

let's see how maxStakeDebt is calculated in `updateAccount`
```solidity
        uint256 portalEnergyIncrease = (accounts[_user].stakedBalance * (maxLockDuration - 
            accounts[_user].lastMaxLockDuration) + (_amount * maxLockDuration)) / SECONDS_PER_YEAR;

accounts[_user].maxStakeDebt += portalEnergyIncrease;
```

If the user has first staked and then the `maxLockDuration` has been increased his maxStakeDebt will be calculated in the following way (considering maxLockDuration has been increased by x)

`(stake * maxLockDuration) / SECONDS_PER_YEAR + (stake * x) / SECONDS_PER_YEAR`

if either of `maxLockDuration` / `x` `stake` are not divisible by `SECONDS_PER_YEAR`, there will be rounding down meaning 

`(stake * maxLockDuration) / SECONDS_PER_YEAR + (stake * x) / SECONDS_PER_YEAR < stake * (maxLockDuration + x) / SECONDS_PER_YEAR`


will later attach coded PoC 


**IMPACT**
Almost any time user tries to call `forceUnstakeAll` and their portalBalance is not enough, it will revert, even if they have the needed tokens to burn
