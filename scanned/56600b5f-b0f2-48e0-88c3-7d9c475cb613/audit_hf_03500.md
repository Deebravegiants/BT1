# [M] No slippage protection for bonders

## Summary
Severity: Medium
Contest weight: 0.6556
Dataset id: 19164
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
When a user calls `bond` or `bondWithDelegate` they specify the amount of DpxEth they want to bond for. As part of this call the cost of the bond (in WETH and rDPX) is calculated. The discount provided for a bond depends on the bond discount factor and the amount of rDPX in the reserve. The bond discount factor should remain relatively static since it is modified only by the admin, but the amount of rDPX in the reserve is constantly fluctuating.

This is therefore a problem, because the discount at the time where the users tries to bond might be different from the actual discount when the transaction is included in a block since the rDPX in the reserve may have changed. Therefore the bonder will end up paying more WETH and/or rDPX for the given amount of bonds than expected.

Since the bonders are still receiving a discount I have lowered the severity of this report from “high” to “medium”, however I still consider this a bug because a bonder might expect/require a certain discount in order to make their whole trading strategy profitable.

## Proof of Concept
For the sake of this report, let’s focus on the normal `bond` path:
```solidity
function bond(
  uint256 _amount,
  uint256 rdpxBondId,
  address _to
) public returns (uint256 receiptTokenAmount) {
  _whenNotPaused();
  // Validate amount
  _validate(_amount > 0, 4);

  // Compute the bond cost
  (uint256 rdpxRequired, uint256 wethRequired) = calculateBondCost(
    _amount,
    rdpxBondId
  );

  IERC20WithBurn(weth).safeTransferFrom(
    msg.sender,
    address(this),
    wethRequired
  );
```
When calling `bond`, the amount of bond to mint is specified, and the cost of those bonds is then calculated with a call to `calculateBondCost` and the WETH transferred from the user (the rDPX is also transferred later). As you can see, there is no way for the user to specify the maximum amount of rDPX or WETH that they want to spend to purchase the bonds.

Now, let’s have a look at the first part of the discount calculation logic:
```solidity
function calculateBondCost(
  uint256 _amount,
  uint256 _rdpxBondId
) public view returns (uint256 rdpxRequired, uint256 wethRequired) {
  uint256 rdpxPrice = getRdpxPrice();

  if (_rdpxBondId == 0) {
    uint256 bondDiscount = (bondDiscountFactor *
      Math.sqrt(IRdpxReserve(addresses.rdpxReserve).rdpxReserve()) *
      1e2) / (Math.sqrt(1e18)); // 1e8 precision
```
As you can see, `bondDiscount` varies with `bondDiscountFactor` and the amount of rDPX in the reserve. Since the user has no control over the rDPX in the reserve, it is possible that this can change from block to block, thereby changing the discount and therefore the WETH & rDPX spent by the user.

This is now a classic “lack of slippage protection” bug that should be resolved as discussed below.

## Recommendation
The `bond` and `bondWithDelegate` should include an additional slippage argument to cap the amount of either WETH or rDPX that they want to spend. Since the ratio of rDPX to WETH is fixed you technically need only a `maxAmount` for one of these; I would suggest `maxRDPX`.

Avoided via adding slippage protection via token approvals, demoting to QA.

While the mitigation suggested by the Sponsor is technically correct, I don’t believe we can reasonably expect end users to use their allowance as a way to express pricing. This is due to the fact that such an operation would not be atomical.

With the information I have available, I believe it is reasonable to say that the execution price is not guaranteed, and since there seems to be a reasonable expectation that no router would be used, the code can cause a leak of value to the caller.

Leading me to believe that Medium Severity is most appropriate.

As mentioned before this can be mitigated via approval checks and will be added to the UI to allow users to know the max cost they would pay for a bond.
