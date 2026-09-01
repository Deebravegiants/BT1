# [M] Some tokens may revert when zero value transfers are made

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-20
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/382
Type: code-finding

## Details
### Lines of code

--------------

[356](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/BaseTOFT.sol#L356-L359), [371](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/BaseTOFT.sol#L371-L374), [145](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/mTapiocaOFT.sol#L145-L148), [272](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTLeverageModule.sol#L272-L275), [252](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/tOFT/modules/BaseTOFTOptionsModule.sol#L252-L255), [116](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/Vesting.sol#L116-L119), [445](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L445-L448), [374](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L374-L380), [506](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/option-airdrop/AirdropBroker.sol#L506-L513), [488](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L488-L494), [527](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/options/TapiocaOptionBroker.sol#L527-L534), [41](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/LTap.sol#L41-L42), [47](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/tokens/LTap.sol#L47-L50), [237](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/usd0/modules/USDOOptionsModule.sol#L237-L240), [794](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Magnetar/modules/MagnetarMarketModule.sol#L794-L797), [159](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/BaseSwapper.sol#L159-L162), [137](https://github.com/Tapioca-DAO/tapioca-periph-audit/blob/023751a4e987cf7c203ab25d3abba58f7344f213/contracts/Swapper/CurveSwapper.sol#L137-L140)

### Vulnerability details

-------------

In spite of the fact that EIP-20 [states](https://github.com/ethereum/EIPs/blob/46b9b698815abbfa628cd1097311deee77dd45c5/EIPS/eip-20.md?plain=1#L116) that zero-valued transfers must be accepted, some tokens, such as LEND will revert if this is attempted, which may cause transactions that involve other tokens (such as batch operations) to fully revert. Consider skipping the transfer if the amount is zero, which will also save gas.

```solidity
File: contracts/tOFT/BaseTOFT.sol

356                  "TOFT_allowed"
357              );
358          }
359:         IERC20(erc20).safeTransferFrom(_fromAddress, address(this), _amount);

371          if (erc20 == address(0)) {
372              _safeTransferETH(_toAddress, _amount);
373          } else {
374:             IERC20(erc20).safeTransfer(_toAddress, _amount);

```



```solidity
File: contracts/tOFT/mTapiocaOFT.sol

145          if (_isNative) {
146              _safeTransferETH(msg.sender, _amount);
147          } else {
148:             IERC20(erc20).safeTransfer(msg.sender, _amount);

```

_Trimmed to 38 lines — full report: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/382_
