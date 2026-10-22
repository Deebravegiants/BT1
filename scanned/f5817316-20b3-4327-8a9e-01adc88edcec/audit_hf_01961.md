# [C] Lack of initialization status check in initialize function

## Summary
Severity: Critical
Contest weight: 0.1984
Dataset id: 10906
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The OjoPTFeed contract includes an initialize function, which is intended to set up the contract's oracle feeds, FEED_1 and FEED_2, after being deployed using OpenZeppelin's clone functionality. This function is important for the contract's operation as it assigns the addresses of the oracle feeds that the contract will use to fetch data. However, the initialize function currently lacks any mechanism to check whether it has already been called, allowing it to be invoked multiple times by any entity. This vulnerability could be exploited by an attacker to replace the legitimate oracle feeds with malicious contracts, potentially leading to the manipulation of data and the draining of any protocol integrating OjoPTFeed.

## Recommendation
It is suggested to implement a mechanism to ensure that the initialize function can only be called once. This can be achieved by checking the value of one of the two feeds, which can be zero only when initialized.
