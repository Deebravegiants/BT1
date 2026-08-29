# [H] PSM token in the Portal contract can be drained by donating PSM token to the Portal contract before calling the  sellPortalEnergy() function

## Summary
Severity: High
Chain: Smart contract
Component: Possum-Labs--Portals-
Published: 2023-11-17
Source: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/40
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** --
**Submission hash (on-chain):** 0x2d3daf59a82dc929597be38c77db14a28238ddc12dba096ecfb85699e6c8129a
**Severity:** high

**Description:**
**Description**\
PSM token in the Portal contract can be drained due to the reserve0 can be manipulated by transferring PSM token directly to the portal contract 

**Attack Scenario**\
1. A malicious actor donate PSM token to the portal contract to manipulate the value of reserve0, so that reserve0 > constantProduct
2. calling the sellPortalEnergy() function, since reserve0 > constantProduct, the calculated result for reserve1 will be 0, thus the calculated result for amountReceived will be equal to reserve0.
3. with 1 wei portalEnergy, the malicious actor  can drain all the PSM tokens from the portal contract

**Attachments**
function sellPortalEnergy(uint256 _amountInput, uint256 _minReceived, uint256 _deadline) external nonReentrant existingAccount {
        /// @dev Require that the input amount is greater than zero
        if (_amountInput == 0) {revert InvalidInput();} 
        
        /// @dev Require that the deadline has not expired
        if (_deadline < block.timestamp) {revert DeadlineExpired();}

        /// @dev Update the stake data of the user
        _updateAccount(msg.sender,0);
        
        /// @dev Require that the user has enough portalEnergy to sell
        if(accounts[msg.sender].portalEnergy < _amountInput) {revert InsufficientBalance();}

        /// @dev Calculate the PSM token reserve (output)
        uint256 reserve0 = IERC20(PSM_ADDRESS).balanceOf(address(this)) - fundingRewardPool;        //@audit-issue : can be manipulated via donation

        /// @dev Calculate the reserve of portalEnergy (input)
        uint256 reserve1 = constantProduct / reserve0;

        /// @dev Calculate the amount of output token received based on the amount of portalEnergy sold
        uint256 amountReceived = (_amountInput * reserve0) / (_amountInput + reserve1);

        /// @dev Require that the amount of output token received is greater than or equal to the minimum expected output

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Possum-Labs--Portals--0xed8965d49b8aeca763447d56e6da7f4e0506b2d3/issues/40_
