# [H] Investor can prevent themselves from being removed by making removeInvestor revert

## Summary
Severity: High
Contest weight: 0.0000
Dataset id: 23393
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Description: The removeInvestor function in RegistryService.sol contains a flaw that allows any investor to
permanently prevent their removal from the system. The function requires that investors[_id].walletCount ==
0 before allowing investor removal, but investors can add unlimited wallets via addWalletByInvestor without any
restrictions, while only EXCHANGE roles can remove wallets via removeWallet.

```solidity
function removeInvestor(string calldata _id) public override onlyExchangeOrAbove investorExists(_id)
returns (bool) {,!
    require(getTrustService().getRole(msg.sender) != EXCHANGE || investors[_id].creator ==
    msg.sender, "Insufficient permissions");,!
    require(investors[_id].walletCount == 0, "Investor has wallets"); <----------
    for (uint8 index = 0; index < 16; index++) {
        delete attributes[_id][index];
    }
    delete investors[_id];
    emit DSRegistryServiceInvestorRemoved(_id, msg.sender);
    return true;
}
```

This creates a permanent DoS condition where malicious investors can add wallets to prevent their own removal

Impact: removeInvestor can be DoS, making an investor unremovable.

## Recommendation
Consider removing addWalletByInvestor.
