# [H] unexpected termination of contract execution whenever the _trade.uid is not found in the array

## Summary
Severity: High
Reporter: seerether
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L234-L241
Type: audit-issue

## Details
# unexpected termination of contract execution whenever the _trade.uid is not found in the array

## Summary
In the _full_close function, when removing the trade UID from the uids array, it uses a pop() operation without checking if the trade UID exists in the array. If the UID is not found in the array, an exception will be raised, which could result in an unexpected termination of the contract execution
## Vulnerability Detail
The vulnerability occurs if the trade's UID is not present in the trades_by_account array. In such a case, the loop completes without finding a match, and when the loop exits, the code encounters the raise statement without any specific exception being raised. This behavior results in an unexpected termination of the contract execution.
## Impact
If the termination happens during the execution of the close_trade function, the funds associated with the trade will not be properly cleaned up, leading to a loss of funds.
## Code Snippet
https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/MarginDex.vy#L234-L241
## Tool used

Manual Review

## Recommendation
Modify the code to check if the trade UID exists in the array before attempting to remove it. If the UID is not found, handle it gracefully by either reverting the transaction or returning an error code. By adding the check for the trade UID's existence and reverting or returning an error message, you can prevent unexpected termination and potential loss of funds.
https://github.com/seerether/Unstoppable/blob/de3a098be0c2414be49612a69346031deebd37c8/unstoppablemitigate3#L2-L15
