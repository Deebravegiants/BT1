# [M] Incorrect setDestinations() Logic in FeeConverterLogic

## Summary
Severity: Medium
Contest weight: 0.4357
Dataset id: 12081
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
DeFi protocols typically have a number of system-wide parameters that can be dynamically conﬁgured on demand. The audited FeeConverter contract is no exception. Speciﬁcally, if we examine the FeeConverter contract, it has deﬁned a number of protocol-wide risk parameters, such as dis.r0, dis.r1, and dis.r3. In the following, we show the corresponding routines that allow for their changes.
```solidity
function setDestinations(address dest0, address dest1, address dest2, uint256 rate0, uint256 rate1, uint256 rate2) external {
    require(msg.sender == owner, "You do not have permission");
    require(rate0 + rate1 + rate2 == 100, "must be 100%");
    require(dest0 != address(0) && dest1 != address(0) && dest2 != address(0), "all cannot address 0");
    if (rate0 == 0) {
        require(dest0 == address(0), "inv0");
    }
    dis.one = dest0;
    dis.r0 = rate0;
    if (rate1 == 0) {
        require(dest1 == address(0), "inv1");
    }
    dis.two = dest1;
    dis.r1 = rate1;
    if (rate2 == 0) {
        require(dest2 == address(0), "inv1");
    }
    dis.three = dest2;
    dis.r2 = rate2;
```
These parameters deﬁne various aspects of the protocol operation and maintenance and need to exercise extra care when conﬁguring or updating them. Our analysis shows the update logic on these parameters can be improved by applying more rigorous sanity checks. For example, current implementation should be revised to ensure these parameters are conﬁgured regardless of the given values of rate0, rate1, and rate2.

## Recommendation
Revise the above routine to ensure these protocol parameters are properly conﬁgured.
