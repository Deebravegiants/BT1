# [M] ```initialize()``` function lacks access control

## Summary
Severity: Medium
Reporter: catchup
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# ```initialize()``` function lacks access control


## Summary
```initialize()``` can be frontrunned.

## Vulnerability Detail
```initialize()``` should only be called by the deployer since it sets the vital state variables.
However, it is a public function which can be called by anyone. Anyone can frontrun the contract deployer and call the ```initialize()```

## Impact
The ownership of the contract would be lost

## Code Snippet
~~~
111:     function initialize(
112:         address _LINK,
113:         address _owner,
114:         uint256 _capacity,
115:         uint256 _startingSharesPerLink
116:     ) public initializer {          //@audit-issue front-runnable initialize. No access control.
117:         LINK = _LINK;
118:         decimals = IERC20Metadata(_LINK).decimals();
119:         owner = _owner;
120:         MAX_CAPACITY = _capacity;
121:         STARTING_SHARES_PER_LINK = _startingSharesPerLink;
122:     }
~~~

## Tool Used
Manual review

## Recommendation
I suggest to include a ```constructor()``` and set the owner as msg.sender within the constructor.
Then include the onlyOwner access control for the ```initialize()``` function.
