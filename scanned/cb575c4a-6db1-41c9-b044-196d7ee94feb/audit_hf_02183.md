# [M] Improved Logic in Handle::removeFxToken()

## Summary
Severity: Medium
Contest weight: 0.4601
Dataset id: 12176
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The handle.fi protocol has an essential contract Handle that stores the main protocol data and configurations. This contract provides public functions that allow authorized admin to dynamically adjust the list of fxTokens supported in the protocol. Accordingly, the setFxToken() and removeFxToken() are these two functions to list and delist a fxToken from the protocol. To elaborate, we show below the removeFxToken() function. This function has a rather straightforward logic in firstly locating the current index of the to-be-removed fxToken, then removing the index from the array by swapping with the last item in the validFxTokens array, and finally emit a related event for off-chain reporting and monitoring.
```solidity
/** @dev Invalidate existing fxToken and remove it from the protocol */
function removeFxToken(address token) external override onlyAdmin {
    uint256 tokenIndex = validFxTokens.length;
    for (uint256 i = 0; i < tokenIndex; i++) {
        if (validFxTokens[i] == token) {
            tokenIndex = i;
            break;
        }
    }
    // Assert that token was found.
    assert(tokenIndex < validFxTokens.length);
    delete isFxTokenValid[token];
    if (tokenIndex < validFxTokens.length - 1) {
        delete validFxTokens[tokenIndex];
        // Replace to-be-deleted item with last element and then pop array.
        validFxTokens[tokenIndex] = validFxTokens[validFxTokens.length - 1];
        validFxTokens.pop();
    } else {
        // Token index is last element, so no need to pop array.
        delete validFxTokens[tokenIndex];
    }
    emit ConfigureFxToken(token);
}
```
Our analysis shows that the above routine can be improved in three aspects. Firstly, the operation on delete validFxTokens[tokenIndex] (line 132) is not necessary as it is immediately overwritten by the following statement (line 134). Secondly, when the to-be-removed fxToken is the last element, the operation on delete validFxTokens[tokenIndex] (line 138) needs to be replaced as validFxTokens.pop(). Thirdly, the final event emit ConfigureFxToken(token) (line 140) is the same as the one emitted when a fxToken is added via setFxToken(). It is helpful to emit different events to differentiate these two actions.

## Recommendation
Improve the above removeFxToken() to properly maintain the list of supported fxTokens in validFxTokens.
