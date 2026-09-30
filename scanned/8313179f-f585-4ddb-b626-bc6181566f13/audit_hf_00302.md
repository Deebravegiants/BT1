# [M] `createRJLaunchEvent`

## Summary
Severity: Medium
Contest weight: 0.4493
Dataset id: 1512
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
function createRJLaunchEvent(
        address _issuer,
        uint256 _phaseOneStartTime,
        address _token,
        uint256 _tokenAmount,
        uint256 _tokenIncentivesPercent,
        uint256 _floorPrice,
        uint256 _maxWithdrawPenalty,
        uint256 _fixedWithdrawPenalty,
        uint256 _maxAllocation,
        uint256 _userTimelock,
        uint256 _issuerTimelock
    ) external override returns (address) {
        require(
            getRJLaunchEvent[_token] == address(0),
            "RJFactory: token has already been issued"
        );
        require(_issuer != address(0), "RJFactory: issuer can't be 0 address");
        require(_token != address(0), "RJFactory: token can't be 0 address");
        require(_token != wavax, "RJFactory: token can't be wavax");
        require(
            _tokenAmount > 0,
            "RJFactory: token amount needs to be greater than 0"
        );
        require(
            IJoeFactory(factory).getPair(_token, wavax) == address(0) ||
                IJoePair(IJoeFactory(factory).getPair(_token, wavax))
                    .totalSupply() ==
                0,
            "RJFactory: liquid pair already exists"
        );
    
        address launchEvent = Clones.clone(eventImplementation);
    
        // msg.sender needs to approve RocketJoeFactory
        IERC20(_token).transferFrom(msg.sender, launchEvent, _tokenAmount);
```

In the current implementation, `RocketJoeFactory.sol#createRJLaunchEvent()` can be called by anyone with at least 1 Wei of `_token`.

This allows a malicious user or attacker to call `createRJLaunchEvent()` with minimal cost and stop others, especially the platform itself or the rightful issuer of the token from creating the RJLaunchEvent.

## Recommendation
Consider making `createRJLaunchEvent()` only callable by the owner of `RocketJoeFactory`.

That’s the spirit, not a single token should be in circulation.
