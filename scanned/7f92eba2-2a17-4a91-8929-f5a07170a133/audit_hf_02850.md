# [C] ProtocolLoses mint() / redeem() FeesDuetoMissingTreasury Collection Mechanism

## Summary
Severity: Critical
Contest weight: 0.2043
Dataset id: 15918
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The contract implements minting and redemption fees in the
custodianMint()
and
redeem()
functions but fails to properly collect and store these fees for the protocol. During minting, the fee
is simply deducted from the minted amount without being allocated to a treasury. Similarly, during
redemption, the fee is subtracted from the redeemed value without being captured. While the fee
calculations are correctly implemented mathematically, the contract lacks both a treasury address
variable and the logic to transfer these fees to protocol-controlled addresses. This creates a sit-
uation where protocol revenue that should be accruing to the project treasury is effectively being
burned or lost.

The protocol loses all potential revenue from its fee structure as they are not being collected.

## Recommendation
Add treasury address state variable and add fees to this variable which are generated through
custodianMint() and redeem()
