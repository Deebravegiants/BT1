# [M] Contract does not earn any boosted position rewards in Maverick Connector

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-04-noya
Published: 2024-05-17
Source: https://github.com/code-423n4/2024-04-noya-findings/issues/1561
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MaverickConnector.sol#L137


# Vulnerability details

## Summary
The contract has a function in MaverickConnector.sol to call [claimBoostedPositionRewards()](https://github.com/code-423n4/2024-04-noya/blob/9c79b332eff82011dcfa1e8fd51bad805159d758/contracts/connectors/MaverickConnector.sol#L137) in order to earn rewards.

**Issue:**
There will be no boosted position rewards since LP tokens received from adding liquidity in maverick pools are never staked in the boosted position contract. 

See here - https://vscode.blockscan.com/ethereum/0x4F24D73773fCcE560f4fD641125c23A2B93Fcb05 and https://docs.mav.xyz/guides/incentives/understanding-boosted-positions. I don't think we even add liquidity to the boosted pool but check. 

We first mint LP tokens through our MAV AMM position through this mint() function https://vscode.blockscan.com/ethereum/0x4F24D73773fCcE560f4fD641125c23A2B93Fcb05 and then we stake() it usin this function https://vscode.blockscan.com/ethereum/0x4F24D73773fCcE560f4fD641125c23A2B93Fcb05. 
## Tools Used
Manual Review

## Recommended Mitigation Steps


## Assessed type

Error
