# [M] The SALT distributions of DAO Reserve and Initial Development Team start from the deployment time rather than the exchange activation time

## Summary
Severity: Medium
Chain: Smart contract
Component: 2024-03-saltyio-mitigation
Published: 2024-03-08
Source: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/125
Type: code-finding

## Details
# Lines of code

https://github.com/othernet-global/salty-io/blob/main/src/dev/Deployment.sol#L213-L214


# Vulnerability details

## Impact
The protocol's reputation could be damaged due to distributing more SALT than expected to the DAO and development team. It's difficult to pinpoint the direct loss, but at the very least, users' willingness to become liquidity providers on Salty may be affected due to unfair initial SALT distribution.

## Proof of Concept
When Salty exchange is actived, 

25M SALT will be transferred to `daoVestingWallet` and 10M SALT will be transferred to `teamVestingWallet` by calling [`InitialDistribution#distributionApproved()`](https://github.com/othernet-global/salty-io/blob/main/src/launch/InitialDistribution.sol#L56-L60):
```solidity
56:	    // 25 million		DAO Reserve Vesting Wallet
57:		salt.safeTransfer( address(daoVestingWallet), 25 * MILLION_ETHER );
58:
59:	    // 10 million		Initial Development Team Vesting Wallet
60:		salt.safeTransfer( address(teamVestingWallet), 10 * MILLION_ETHER );
```
- `daoVestingWallet` is responsible for distributing 25M SALT to `DAO` linely over 10 years
- `teamVestingWallet` is responsible for distributing 10M SALT to `teamWallet` linely over 10 years
Check the smart contract deployments in [Deployment.sol](https://github.com/othernet-global/salty-io/blob/main/src/dev/Deployment.sol#L213-L214):
```solidity
213:		daoVestingWallet = new VestingWallet( address(dao), uint64(block.timestamp), 60 * 60 * 24 * 365 * 10 );
214:		teamVestingWallet = new VestingWallet( teamWallet, uint64(block.timestamp), 60 * 60 * 24 * 365 * 10 );
```
As we can see, the distribution start time of `daoVestingWallet` and `teamVestingWallet` is the deployment time. However the exchange is not active at the moment. 
If we check line 216 in [Deployment.sol](https://github.com/othernet-global/salty-io/blob/main/src/dev/Deployment.sol#L216), we can see that it will take at least 5 days to active the exchange because `ballotDuration` was initialized to `5 days`.
```solidity
		bootstrapBallot = new BootstrapBallot(exchangeConfig, airdrop, 60 * 60 * 24 * 5 );
```
From the above we can see, `DAO` and `teamWallet` can get 5 days SALT distribution immediately once the exchanged is active.

Copy below codes to [BootstrapBallot.t.sol](https://github.com/othernet-global/salty-io/blob/main/src/launch/tests/BootstrapBallot.t.sol) and run `COVERAGE="yes" NETWORK="sep" forge test -vv --rpc-url RPC_URL --match-test test_finalizeBallotThenCheckVestingBalance`

```solidity
```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2024-03-saltyio-mitigation-findings/issues/125_
