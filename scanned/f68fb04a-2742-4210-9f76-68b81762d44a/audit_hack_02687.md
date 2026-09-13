# [M] Missing non zero check when setting STARTING_SHARES_PER_LINK

## Summary
Severity: Medium
Reporter: catchup
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Missing non zero check when setting STARTING_SHARES_PER_LINK


## Summary
```STARTING_SHARES_PER_LINK``` is set in the ```initialize()``` function, but there is no non-zero check, which may lead to divide by zero.

## Vulnerability Detail
If ```STARTING_SHARES_PER_LINK``` is set to zero by mistake, and the ```totalShares == 0```, division in ```convertToTokens()``` function would revert because of divide by zero.

## Impact
This would result in revert of ```convertToTokens()```.


## Code Snippet
~~~
111:     function initialize(
112:         address _LINK,
113:         address _owner,
114:         uint256 _capacity,
115:         uint256 _startingSharesPerLink
116:     ) public initializer {
117:         LINK = _LINK;
118:         decimals = IERC20Metadata(_LINK).decimals();
119:         owner = _owner;
120:         MAX_CAPACITY = _capacity;
121:         STARTING_SHARES_PER_LINK = _startingSharesPerLink;  //@audit-issue no-zero check for _startingSharesPerLink. If STARTING_SHARES_PER_LINK is set to zero line 604 will be divide by 0
122:     }
~~~

~~~
601:     function convertToTokens(uint256 _shares) public view returns (uint256) {
602:         uint256 shareSupply = totalShares; // saves one SLOAD
603:         if (shareSupply == 0) {
604:             return _shares / STARTING_SHARES_PER_LINK;
605:         }
606:         return _shares.mulDivDown(totalSupply(), shareSupply);
607:     }
~~~

## Tool Used
Manual review

## Recommendation
I suggest to include a non-zero check for ```_startingSharesPerLink``` in the ```initialize()```.
