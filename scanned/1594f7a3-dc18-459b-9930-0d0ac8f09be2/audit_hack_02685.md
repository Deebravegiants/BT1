# [M] Uncontrolled update of the ownership can lock many features

## Summary
Severity: Medium
Reporter: catchup
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Uncontrolled update of the ownership can lock many features


## Summary
There are no controls while setting the ```owner``` address. This may cause the ownership to be lost. 

## Vulnerability Detail
Owner is first set by the ```initialize()``` function and then can be transferred to another address via ```transferOwnership()``` function only by the current owner.
Firstly, it can be set to a wrong address during calling the ```initialize()```. There is no zero-check control here.
Secondly, it can be set to a faulty address by the ```transferOwnership()``` function.

## Impact
Owner has important privileges such as authorization for the upgrades, adding and removing plugins, rebalancing the plugins and setting the max capacity.
Once the ownership is lost, access to all these features will be lost and can not be recovered. Even the contract can not be upgraded, so the contract would be completely useless.

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
119:         owner = _owner;                                     //@audit-issue owner non zero check
120:         MAX_CAPACITY = _capacity;
121:         STARTING_SHARES_PER_LINK = _startingSharesPerLink;
122:     }
~~~

~~~
295:     function transferOwnership(address _newOwner) external onlyOwner {      //@audit-issue 2-step ownership transfer
296:         owner = _newOwner;
297:         emit OwnershipTransferred(msg.sender, _newOwner);
298:     }
299: 
~~~


## Tool Used
Manual review

## Recommendation
A zero address check can be included in the ```initialize()``` but still this does not eliminate the risk of inputting a faulty address as an argument.
Therefore, I suggest to include a ```constructor()``` and set the owner as msg.sender within the constructor.
Then the transfer of the ownership can be made as a 2-step process; where current owner sets the pendingOwner address and pendingOwner claims the ownership.
