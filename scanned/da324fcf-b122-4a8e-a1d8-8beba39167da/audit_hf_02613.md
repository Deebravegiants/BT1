# [M] Not supporting IERC1155Receiver interface ID

## Summary
Severity: Medium
Contest weight: 0.6944
Dataset id: 14092
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DineroTreasuryConnector inherits from ERC1155HolderUpgradeable, which implements ERC-165 to support the IERC1155Receiver interface ID. also inherits from AccessControlDefaultAdminRulesUpgradeable, which implements ERC-165 to support the IAccessControlDefaultAdminRules interface ID. But the current implementation of supportsInterface interface within DineroTreasuryConnector remove IERC1155Receiver interface ID from ERC-165 checker.
```solidity
contract DineroTreasuryConnector is IDineroTreasuryConnector, ERC1155HolderUpgradeable, Acce
// ...
function initialize() public initializer {
    __AccessControlDefaultAdminRules_init(1 days, msg.sender);
    __ERC1155Holder_init();
}

function supportsInterface(
    bytes4 _interfaceId
) public view virtual override(ERC1155HolderUpgradeable, AccessControlDefaultAdminRulesUpgradeable)
    public view virtual override(ERC1155HolderUpgradeable, AccessControlDefaultAdminRulesUpgradeable
    return super.supportsInterface(_interfaceId);
// ...
```
The reason is due to multiple inheritance, as supportsInterface is present in both ERC1155HolderUpgradeable and AccessControlDefaultAdminRulesUpgradeable, which are inherited by DineroTreasuryConnector. The super call will trigger the right-most contract, which is AccessControlDefaultAdminRulesUpgradeable, because Solidity inheritance is linearized from right to left. As a result, if any contracts check whether DineroTreasuryConnector supports IERC1155Receiver using ERC-165, it will return false. PoC:
```solidity
describe("Check ERC165 interface", async () => {
    "checkinterfaceidofERC1155ReceiverandAccessControlDefaultAdminRules", async () => {
        // given
        const {owner, treasury} = await loadFixture(deployOrGetFixture);
        // when
        // ERC1155 interfaceId : 0x4e2312e0
        const result = await treasury.supportsInterface("0x4e2312e0");
        // AdminRules interfaceId : 0x31498786
        const result2 = await treasury.supportsInterface("0x31498786");
        // then
        expect(result).is.false;
        expect(result2).is.true;
    }
});
```

## Recommendation
Modify DineroTreasuryConnector's supportsInterface to the following:
```solidity
function supportsInterface(
    bytes4 _interfaceId
) public view virtual override(ERC1155HolderUpgradeable, AccessControlDefaultAdminRulesUpgradeable)
    public view virtual override(ERC1155HolderUpgradeable, AccessControlDefaultAdminRulesUpgradeable
- return super.supportsInterface(_interfaceId);
+ return _interfaceId == type(IERC1155Receiver).interfaceId || super.supportsInterface(_interfaceId);
```
