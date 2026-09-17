# [M] .transfer is not safe to use with custom smart contracts

## Summary
Severity: Medium
Source: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Address.sol#L53-L59
Type: audit-issue

## Details
# Handle

paulius.eth


# Vulnerability details

## Impact
.transfer is used for transferring ether. It is no longer recommended as recipients with custom fallback functions (smart contracts) will not be able to handle that. You can read more here: https://consensys.net/diligence/blog/2019/09/stop-using-soliditys-transfer-now/

## Recommended Mitigation Steps
Solution (don't forget re-entrancy protection): https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/Address.sol#L53-L59
