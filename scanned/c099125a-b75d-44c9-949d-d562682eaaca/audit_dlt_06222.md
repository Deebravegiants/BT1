# [M] No slippage check in deposit function could result in an unexpected loss of shares for users

## Summary
Severity: Medium
Chain: Smart contract
Component: ether-fi
Published: 2023-11-08
Source: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/30
Type: hats-finding

## Details
**Github username:** @JJtheAndroid
**Submission hash (on-chain):** 0x01d92d79e47e59e50e7f5c149b8e2dd32aa379040a44a9db4d818ba01fe69b7a
**Severity:** medium

**Description:**
**Description**\
No slippage check in deposit and withdraw function can result in griefing attacks/race conditions

**Attack Scenario**\

The deposit function shown below, allows a user to deposit their funds. 

    function deposit(address _referral) public payable whenNotPaused returns (uint256) {
        require(_isWhitelisted(msg.sender), "Invalid User");


        emit Deposit(msg.sender, msg.value, SourceOfFunds.EETH, _referral);


        return _deposit();
    }


It uses the nested function sharesforDepositAmount to calculates how much shares a user gets for their ETH

https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/blob/ec7d11c943b545994cd3266b9aa17affde754d9e/src/LiquidityPool.sol#L614-L620


Here we see that the calculation relies on the function getTotalPooledEther (totalValueOutOfLp +totalValueInLp ) which can be changed by the function deposit, withdraw and batchCancelDeposit. WHen getTotalPooledEther is increased , the shares received is decreased (assuming that the deposit size is still the same)


This can leave an unsuspecting victim vulnerable to a griefing attack where the victim will recieve less shares than what they originally thought


Scenario:

1. Victim tries to call deposit 
2. Attacker see the transaction and front runs the victim by calling deposit first, changing the value of getTotalPooledEther 

_Trimmed to 38 lines — full report: https://github.com/hats-finance/ether-fi-0x36c3b77853dec9c4a237a692623293223d4b9bc4/issues/30_
