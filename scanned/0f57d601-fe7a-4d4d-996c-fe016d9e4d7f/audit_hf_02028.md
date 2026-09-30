# [H] Proper Dividend Accounting In ERC1155DividentToken

## Summary
Severity: High
Contest weight: 0.6368
Dataset id: 11566
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
To facilitate the fixed-rate yield generation, the 88mph protocol makes use of the ERC1155DividentToken
contract to allow for efficient distribution of dividends to all holders of an token ID. The specific token
contract also supports multiple dividend tokens. In the following, we examine this token contract
implementation.
To elaborate, we show below the _beforeTokenTransfer() routine in the ERC1155DividentToken
token contract.
This routine is invoked for every token transfer to properly keep track of due
dividends for holders. Specifically, it discerns three different scenarios, i.e., Mint, Burn, and Transfer.
It comes to our attention that the Burn-related handling logic is flawed.
```solidity
function _beforeTokenTransfer(
    address operator,
    address from,
    address to,
    uint256[] memory ids,
    uint256[] memory amounts,
    bytes memory data
) internal virtual override(ERC1155Base) {
    super._beforeTokenTransfer(operator,
    from,
    to,
    ids,
    amounts,
    data);
    if (from == address(0)) {
        // Mint
        for (uint256 i = 0; i < ids.length; i++) {
            uint256 tokenID = ids[i];
            uint256 amount = amounts[i];
            for (uint256 j = 1; j <= dividendTokenDataListLength; j++) {
                DividendTokenData storage dividendTokenData =
                dividendTokenDataList[j];
                dividendTokenData.magnifiedDividendCorrections[tokenID][from] = (dividendTokenData.magnifiedDividendPerShare[tokenID] * amount)
                .toInt256();
            }
        }
    } else if (to == address(0)) {
        // Burn
        for (uint256 i = 0; i < ids.length; i++) {
            uint256 tokenID = ids[i];
            uint256 amount = amounts[i];
            for (uint256 j = 1; j <= dividendTokenDataListLength; j++) {
                DividendTokenData storage dividendTokenData =
                dividendTokenDataList[j];
                dividendTokenData.magnifiedDividendCorrections[tokenID][from] += (dividendTokenData.magnifiedDividendPerShare[tokenID] * amount)
                .toInt256();
            }
        }
    } else {
        // Transfer
        for (uint256 i = 0; i < ids.length; i++) {
            uint256 tokenID = ids[i];
            uint256 amount = amounts[i];
            for (uint256 j = 1; j <= dividendTokenDataListLength; j++) {
                DividendTokenData storage dividendTokenData =
                dividendTokenDataList[j];
                int256 _magCorrection =
                (dividendTokenData.magnifiedDividendPerShare[tokenID] * amount)
                .toInt256();
                // Retain the rewards
                dividendTokenData.magnifiedDividendCorrections[tokenID][from] += _magCorrection;
                dividendTokenData.magnifiedDividendCorrections[tokenID][to] = _magCorrection;
            }
        }
    }
}
```
Specifically, in the Burn case, the related state of magnifiedDividendCorrections[tokenID] for the from should be updated, instead of the current to! A non-updated magnifiedDividendCorrections[tokenID] for the from account may result in potential loss for the sender.

## Recommendation
Revise the above _beforeTokenTransfer() logic to properly update dividend correction for associated parties in all cases.
