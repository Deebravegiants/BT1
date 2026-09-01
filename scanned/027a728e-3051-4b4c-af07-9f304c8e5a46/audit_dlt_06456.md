# [H] Campaign owners can bypass protocol fees causing loss to the protocol

## Summary
Severity: High
Chain: Smart contract
Component: Metrom
Published: 2024-05-22
Source: https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/issues/33
Type: hats-finding

## Details
**Github username:** --
**Twitter username:** MrPotatoMagic
**Submission hash (on-chain):** 0xfcf2a6255e63dea3a403ddb365b3533f0d48147b47361df787c714dadc160d33
**Severity:** high

**Description:**
**Description**\
We know that when a campaign is created, the code [here](https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/Metrom.sol#L193C1-L216C14) applies protocol fees if the resolved fee [here](https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/Metrom.sol#L161) for the msg.sender (i.e. campaign owner) is set to some non-zero value. We can see the interface mentioning this for the SpecificFee struct as well [here](https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/IMetrom.sol#L23C1-L31C2)

**Attack Scenario:**

The issue in the current code is that the campaign owner (who is expected to be charged) can use another address to create the campaign. This is possible by calling the [createCampaigns()](https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/Metrom.sol#L160) function by using the other address since it would simply set the campaign owner to the msg.sender [here](https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/Metrom.sol#L183).

The owner can then just use the other address (which is the current campaign owner) to transfer the ownership to the original owner (who was expected to be charged).

Since the transferCampaignOwnership() and acceptCampaignOwnership() functions [here](https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/Metrom.sol#L324C1-L339C6) do not check if the new owner has campaign specific fees applied, it just simply allows transferring the ownership of the campaign.

This overall means that campaign owners can avoid paying fees to the protocol, thus causing loss to them.

**Link to code**

See here - https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/Metrom.sol#L324C1-L339C6

See here - https://github.com/hats-finance/Metrom-0xfdfc6d4ac5807d7460da20a3a1c0c84ef2b9c5a2/blob/e9d6b1e594d5bb3694bfe68f73399156ebb5d3a4/src/Metrom.sol#L160


**Mitigation:**
If the new owner's fees are greater than the current owner's fees, consider charging the difference between the new owner's fees and current owner's fees to ensure the protocol receives the right amount.

If the new owner's fees are less than the current owner's fees, consider not charging since the current owner has already paid for the campaign fees. This prevents overcharging of fees.

In both cases, take the fees only once the new owner calls acceptOwnership().
