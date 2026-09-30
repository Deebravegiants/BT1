# [M] Protocol admin account has a large centralization attack surface

## Summary
Severity: Medium
Contest weight: 0.1464
Dataset id: 3393
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A malicious or a compromised admin can execute various rug-like attacks on the protocol: 1. Upgrading the Babylon7Core contract to add code to exploit creator's allowances so their raffled items are stolen by the protocol owner 2. Setting the _treasury address to one without a payable fallback or receive method (for example address(0)), resulting in an inability for the listing.creator to execute a transferETHToCreator transaction 3. Setting an owner-controlled random provider at any time, so controlling who the winner of a raffle is There are also smaller problems, like: 1. Setting a very small _maxListingDuration 2. Setting a very large _minDonationBps (both in initialize and in setMinDonationBps) 3. The core address can be changed in RandomProvider which can allow for direct calls to requestRandom

## Recommendation
Use a TimeLock contract to be the protocol owner, so users can actually monitor protocol upgrades or other actions by the admins. Another option is to make the admin a governance controlled address. Also you should use a MINIMUM_MAX_LISTING_DURATION constant and validate the maxListingDuration value in setMaxListingDuration, doing the same with a MAXIMUM_MIN_DONATION_BPS constant in both initialize and setMinDonationBps for the minDonationBps value. Finally, the setBabylon7Core should be made so it is called only once and core can't be changed later.
