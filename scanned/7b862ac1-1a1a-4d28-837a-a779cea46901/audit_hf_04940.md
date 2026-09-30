# [M] Lack of execution fee mechanism in Account-

## Summary
Severity: Medium
Contest weight: 0.4090
Dataset id: 22885
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When the keeper execute executeWithdraw or cancelWithdraw, no execution fee is payed for the keeper.
In OrderFacet and StakeFaucet, when the keepers execute increase order/ stake tokens, there will be some execution fee for the keepers. However, in AccountFacet, we lack of execution fee mechanism. Considering if gas price increases or there is not enough motivation to trigger executeWithdraw or cancelWithdraw. This will cause traders' redeem may be blocked.
```solidity
function executeWithdraw(uint256 requestId, OracleProcess.OracleParam[] calldata oracles) external override {
    RoleAccessControl.checkRole(RoleAccessControl.ROLE_KEEPER);
    Withdraw.Request memory request = Withdraw.get(requestId);
    if (request.account == address(0)) {
    }
    OracleProcess.setOraclePrice(oracles);
    AssetsProcess.executeWithdraw(requestId, request);
    OracleProcess.clearOraclePrice();
}
```
The keepers has less motivation to trigger executeWithdraw or cancelWithdraw compared with other operations. This will block the traders' collateral withdraw.

## Recommendation
Add execution fee mechanism for AccountFacet.
