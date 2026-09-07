# [H] Crosslinking transaction attack

## Summary
Severity: High
Chain: Hyperledger Fabric
Component: hyperledger/fabric
CVE: CVE-2023-46132
Published: 2023-11-14
Source: https://github.com/hyperledger/fabric/security/advisories/GHSA-v9w2-543f-h69m
Type: github-advisory

## Details
# Short summary

Combining two molecules to one another, called "cross-linking" results in a molecule with a chemical formula that is composed of all atoms of the original two molecules. 

In Fabric, one can take a block of transactions and cross-link the transactions in a way that alters the way the peers parse the transactions. If a first peer receives a block `B` and a second peer receives a block identical to `B` but with the transactions being cross-linked, the second peer will parse transactions in a different way and thus its world state will deviate from the first peer. 

Orderers or peers cannot detect that a block has its transactions cross-linked, because there is a vulnerability in the way Fabric hashes the transactions of blocks. It simply and naively concatenates them, which is insecure and lets an adversary craft a "cross-linked block" (block with cross-linked transactions) which alters the way peers process transactions. 
For example, it is possible to select a transaction and manipulate a peer to completely avoid processing it, without changing the computed hash of the block.

Additional validations have been added in v2.2.14 and v2.5.5 to detect potential cross-linking issues before processing blocks.

## Impact
In V1 and V2, we only have a crash fault tolerant orderer and as such, the security model Fabric operates in is that the orderer is honest,
but peers may be malicious. As such, a peer that replicates a block from a malicious peer can have a state fork.

In V3 which we did not a release a GA yet (only a preview), we have a byzantine fault tolerant orderering service, so the security model that Fabric operates in such a case includes malicious orderers. If the orderer is malicious, it can cause state forks for peers, and can infect non-malicious orderers with cross-linked blocks.

# Long summary



In order to create a signature on a big chunk of data  such as a block, the data needs to be "compressed" first to the input size of the signature algorithm.

In Fabric's case, we use a hash function which compressed a Fabric block from arbitrary size to a 32 byte string.

 

In order to understand the problem we need to be more specific: The block structure has three parts to it: (1) Header, (2) Transactions, and (3) Metadata.

When hashing the block, the header and metadata are stitched together and then hashed, and this hash of the header and the metadata is what signed (it's a simplification but let's not get into details)

However, the transactions of the block are not part of the above hash. Instead, the header contains a hash, called the "Data hash" and despite the fact that in the comments it is said: "// The hash of the BlockData, by MerkleTree", actually it is far from being the case, and that is where our problem lies.

The problem is that the way the transactions are hashed gives an attacker some freedom in manipulating the data. 

To create the Data Hash, the transactions in the block are concatenated to one another, creating a big long byte array and then this big long byte array is hashed, and this is essentially the Data Hash.

The transactions in the block are a list of raw byte arrays, and when they are concatenated they look like this:

_Trimmed to 38 lines — full report: https://github.com/hyperledger/fabric/security/advisories/GHSA-v9w2-543f-h69m_
