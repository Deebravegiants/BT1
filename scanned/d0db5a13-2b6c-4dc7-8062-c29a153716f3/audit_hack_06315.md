# [M] Refund after bounty close can cause DOS

## Summary
Severity: Medium
Reporter: minhtrng
Source: https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/DepositManager/Implementations/DepositManagerV1.sol#L152-L195
Type: audit-issue

## Details
# Refund after bounty close can cause DOS

## Summary

If a depositor performs a refund after a competition has closed this can DOS claiming.

## Vulnerability Detail

Deposits can be refunded even after a bounty is closed. According to the docs, this is by design, to avoid funds being stuck when not claimed. However, this can cause DOS scenario for the tiered bounties.

For the `TieredFixedBounty` assume the scenario where the network token (e.g. ETH for Ethereum) is used to payout the tier winners. The funding goal has been set to 10 ETH, with the distribution to the winners being 1st -> 5ETH, 2nd -> 3ETH and 3rd -> 2ETH. Of the 10 ETH goal, 4 ETH have been provided by Alice. After the contest has finished, one of the winners goes ahead to claim his price by calling `ClaimManager.permissionedClaimTieredBounty` and closes the contest as a result:

```js
//in _claimTieredFixedBounty used by permissionedClaimTieredBounty
if (_bounty.status() == 0) { 
    _bounty.closeCompetition();
```

Now, Alice decides to withdraw her 4 ETH (e.g. out of malice), leaving the contract underfunded, meaning that one of the participants will not be able to claim the funds they were entitled to, after performing their work. Since the contest is closed, new deposits can not be made:

```js
//DepositManager
function fundBountyToken(
    ...
    require(bountyIsOpen(_bountyAddress), Errors.CONTRACT_ALREADY_CLOSED);
```

Funding the contract to compensate for the deficit by directly transferring tokens would also not be possible for this case since the `receive` function forbids that:

```js
/// @notice receive() method to accept protocol tokens
receive() external payable {
    revert(
        'Cannot send Ether directly to boutny contract. Please use the BountyV1.receiveFunds() method.'
    );
}
```

Hypothetically, one could still fill up the contract by using the `selfdestruct` feature, but this is currently discussed on being removed entirely.

The same case can be made for `TieredPercentageBounty`, even though there are even more possible scenarios here, due to the possibility of adding custom tokens. 

## Impact

Claimant is not able to withdraw the funds even though they are eligible for it.

## Code Snippet

https://github.com/sherlock-audit/2023-02-openq/blob/fc2dae7107e4be0878ace40b1e7218c18e1933fe/contracts/DepositManager/Implementations/DepositManagerV1.sol#L152-L195

## Tool used

Manual Review

## Recommendation
Claimants should be guaranteed to be able to withdraw their share of the deposited funds after a competition closed from a business level perspective. To still enable that funds wont get stuck if a claimant does not claim, add a grace period in which only claimants can withdraw, while depositors can do so after said period has ended.
