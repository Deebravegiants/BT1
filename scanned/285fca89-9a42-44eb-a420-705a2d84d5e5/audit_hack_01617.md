# [M] Opyn incident: Opyn, an on-chain options platform, disclosed that its Ethereum put options were maliciously exploited by external participants. O

## Summary
Severity: Medium
Target: Opyn
Loss: 371,260 USDC
Attack method: Contract Vulnerability
Published: 2020-08-04
Source: https://medium.com/opyn/opyn-eth-put-exploit-c5565c528ad2
Type: slowmist-incident

## Details
Opyn, an on-chain options platform, disclosed that its Ethereum put options were maliciously exploited by external participants. Opyn pointed out that all other Opyn contracts except Ethereum put options are not affected by this vulnerability. The attacker doubled the use of oToken and stole the mortgage assets of the put option seller. According to Opyn statistics, a total of 371,260 USDC has been stolen so far. Because the exercise function exercise() in the Opyn ETH Put smart contract does not perform real-time verification of the trader's ETH. According to the business logic of the Opyn platform, the buyer of the put option transfers the corresponding value of ETH to the seller to obtain the digital asset mortgaged by the seller. The cunning attacker first initiates a disguised transaction to himself, and uses the reusable feature of this ETH to initiate a transfer to the seller user again, thereby defrauding the seller's mortgaged digital assets.
