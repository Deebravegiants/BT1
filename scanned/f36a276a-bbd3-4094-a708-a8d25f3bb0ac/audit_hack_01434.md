# [M] OpenSea incident: A vulnerability in NFT marketplace OpenSea resulted in at least 42 NFTs being sent to a burn address, worth at least $100,000. The

## Summary
Severity: Medium
Target: OpenSea
Loss: $ 100,000
Attack method: Contract Vulnerability
Published: 2021-09-10
Source: http://chainb.com/?P=Cont&amp;id=32317
Type: slowmist-incident

## Details
A vulnerability in NFT marketplace OpenSea resulted in at least 42 NFTs being sent to a burn address, worth at least $100,000. The issue was first raised by Nick Johnson, lead developer of the Ethereum Name Service (ENS), who noted that when he transferred an ENS domain name (in the form of an NFT), it was transferred to a burn address. This means it was accidentally sent to an uncontrolled address and can no longer be moved. Regarding the destroyed ENS domain name, Johnson said it was the first registered ENS domain name, called rilxxlir.eth, which was held by an ENS account when Johnson registered it with personal funds. In order to transfer the ENS domain name to his own account, he went to OpenSea to perform the transfer, only to find that it had been sent to a destruction address by mistake. Since Johnson is still the controller of the ENS domain name, he can still make changes, just cannot move the domain name. Johnson then received further reports from others who were similarly affected and compiled a list of 32 affected transactions involving 42 NFTs. Most NFTs use the ERC-721 standard, but a few use ERC-1155. He looked at the floor price of each NFT, which totaled about $100,000. Johnson claims that OpenSea has now fixed the vulnerability.
