# [M] MetaMask incident: @alxlpsc disclosed on medium that MetaMask has serious privacy leaks. The vulnerability mainly uses MetaMask to automatically load

## Summary
Severity: Medium
Target: MetaMask
Loss: -
Attack method: Information Leakage
Published: 2022-01-20
Source: https://medium.com/@alxlpsc/critical-privacy-vulnerability-getting-exposed-by-metamask-693c63c2ce94
Type: slowmist-incident

## Details
@alxlpsc disclosed on medium that MetaMask has serious privacy leaks. The vulnerability mainly uses MetaMask to automatically load NFT image URLs. Basic attack idea: the attacker can set the URI of the NFT to a server URL that he can control, and transfer the NFT to the target account; when the user logs in to MetaMask, MetaMask will automatically scan the NFT owned by the account, and initiate a pointer to The HTTP request to the attacker's server; the attacker can obtain the victim's IP information from the access log.
