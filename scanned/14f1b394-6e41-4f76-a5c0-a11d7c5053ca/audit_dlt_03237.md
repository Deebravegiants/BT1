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



```solidity
File: contracts/tOFT/modules/BaseTOFTLeverageModule.sol

272          if (erc20 == address(0)) {
273              _safeTransferETH(_toAddress, _amount);
274          } else {
275:             IERC20(erc20).safeTransfer(_toAddress, _amount);

```



```solidity
File: contracts/tOFT/modules/BaseTOFTOptionsModule.sol

252                  })
253              );
254          } else {
255:             IERC20(tapSendData.tapOftAddress).safeTransfer(from, tapAmount);

```



```solidity
File: contracts/Vesting.sol

116          users[msg.sender].claimed += _claimable;
117          users[msg.sender].latestClaimTimestamp = block.timestamp;
118  
119:         token.safeTransfer(msg.sender, _claimable);

```



```solidity
File: contracts/governance/twTAP.sol

445          totals.totalDistPerVote[_rewardTokenId] +=
446              (_amount * DIST_PRECISION) /
447              uint256(totals.netActiveVotes);
448:         rewardToken.safeTransferFrom(msg.sender, address(this), _amount);

```



```solidity
File: contracts/option-airdrop/AirdropBroker.sol

374          unchecked {
375              for (uint256 i = 0; i < len; ++i) {
376                  ERC20 paymentToken = ERC20(_paymentTokens[i]);
377                  paymentToken.transfer(
378                      paymentTokenBeneficiary,
379                      paymentToken.balanceOf(address(this))
380:                 );

506              _paymentToken.decimals()
507          );
508  
509          _paymentToken.transferFrom(
510              msg.sender,
511              address(this),
512              discountedPaymentAmount
513:         );

```



```solidity
File: contracts/options/TapiocaOptionBroker.sol

488          unchecked {
489              for (uint256 i = 0; i < len; ++i) {
490                  ERC20 paymentToken = ERC20(_paymentTokens[i]);
491                  paymentToken.transfer(
492                      paymentTokenBeneficiary,
493                      paymentToken.balanceOf(address(this))
494:                 );

527              _paymentToken.decimals()
528          );
529  
530          _paymentToken.transferFrom(
531              msg.sender,
532              address(this),
533              discountedPaymentAmount
534:         );

```



```solidity
File: contracts/tokens/LTap.sol

41       function deposit(uint256 amount) external {
42:          tapToken.transferFrom(msg.sender, address(this), amount);

47           require(block.timestamp > lockedUntil, "Still locked");
48           uint256 amount = balanceOf(msg.sender);
49           _burn(msg.sender, amount);
50:          tapToken.transfer(msg.sender, amount);

```



```solidity
File: contracts/usd0/modules/USDOOptionsModule.sol

237                  })
238              );
239          } else {
240:             IERC20(tapSendData.tapOftAddress).safeTransfer(from, tapAmount);

```



```solidity
File: contracts/Magnetar/modules/MagnetarMarketModule.sol

794          address _token,
795          uint256 _amount
796      ) private {
797:         IERC20(_token).safeTransferFrom(_from, address(this), _amount);

```



```solidity
File: contracts/Swapper/BaseSwapper.sol

159              );
160              return amount;
161          }
162:         IERC20(token).safeTransferFrom(msg.sender, address(this), amount);

```



```solidity
File: contracts/Swapper/CurveSwapper.sol

137                  0
138              );
139          } else {
140:             IERC20(tokenOut).safeTransfer(to, amountOut);

```


### Assessed type

------------

other
