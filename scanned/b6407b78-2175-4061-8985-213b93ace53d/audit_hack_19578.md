# [H] ` YoloV2  :: rolloverETH` User can get selected after they moved eth to another rounds  and cause a Dos attack

## Summary
Severity: High
Reporter: Cheesy Tawny Osprey
Source: https://github.com/sherlock-audit/2024-01-looksrare/blob/main/contracts-yolo/contracts/YoloV2.sol#L643
Type: audit-issue

## Details
# ` YoloV2  :: rolloverETH` User can get selected after they moved eth to another rounds  and cause a Dos attack

## Summary
 User can get selected after they moved eth to another rounds  and cause a Dos attack 

## Impact
loss of funds
## Code Snippet
https://github.com/sherlock-audit/2024-01-looksrare/blob/main/contracts-yolo/contracts/YoloV2.sol#L643
## Tool used

Manual Review

## Recommendation
remove user id from round
