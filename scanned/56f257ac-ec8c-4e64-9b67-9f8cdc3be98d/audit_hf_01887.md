# [H] The total supply of NFTs might not be fully minted

## Summary
Severity: High
Contest weight: 0.8039
Dataset id: 10464
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The protocol implements a classic NFT contract with the addition of generations. The first generation is the 0th generation and it is the only one that can be minted. All other generations are minted only via breeding of previous generations. In the current state, the total supply for the 0th generation is 150. However, there is a scenario in which the total amount may NOT be minted and it may not be possible for it to be minted. If we take a look at the mint function there are two branches that can be used to mint depending on the isBatch flag.
```solidity
if (isBatch) {
    // Batch minting logic
    require( // 100 / 10
        mintedBatches < BATCH_SUPPLY / BATCH_SIZE,
        "All batches have been minted"
    );
    require(quantity == BATCH_SIZE, "Batch size must be 10");
    require(
        totalMinted + quantity <= BATCH_SUPPLY, // 100
        "Exceeds batch supply limit"
    );
    for (uint i = 0; i < quantity; i++) {
        _mintSingleNFT(msg.sender, tokenUri[i], genes[i]);
    }
    mintedBatches += 1;
} else {
    // Release-based minting logic
    require(totalReleases <= 5, "Exceeds total releases");
    require(
        totalMinted + quantity <= TOTAL_SUPPLY,
        "Exceeds total supply"
    );
    require(quantity > 0 && quantity <= 10, "Invalid release size");
    for (uint i = 0; i < quantity; i++) {
        _mintSingleNFT(msg.sender, tokenUri[i], genes[i]);
    }
    totalReleases += 1;
    releaseSizes[totalReleases] = quantity;
}
```
If the isBatch flag is set to true 10 NFTs are minted. There are 10 batches in total - so 100 NFTs can be minted via batch. The other branch of minting is release-based where there can be a maximum of 6 releases for 50 NFTs left. Here however a user may mint only a single NFT. If the 50 NFTs that are NOT minted from these 6 releases they are lost forever. This is enforced by the require(totalReleases <= 5, "Exceeds total releases"); statement, and the totalReleases variable is incremented at the end of the function. Another way to NOT mint all NFTs is again if less than 10 NFTs are minted by the release-based minting logic before the batch minting logic. This is caused because the batch minting logic compares the totalMinted amount plus the current quantity against the batch supply, NOT the total supply.

## Recommendation
Remove the total releases max 5 requirement, as the total supply is kept in check by the require(totalMinted + quantity <= TOTAL_SUPPLY, "Exceeds total supply"); statement. When batch minting, compare the totalMinted + quantity against the total supply. The maxim minted by batches is already enforced by the mintedBatches < BATCH_SUPPLY / BATCH_SIZE require statement.
```solidity
if (isBatch) {
    // Batch minting logic
    require(mintedBatches < BATCH_SUPPLY / BATCH_SIZE, "All batches have been minted");
    require(quantity == BATCH_SIZE, "Batch size must be 10");
    // require(totalMinted + quantity <= BATCH_SUPPLY, "Exceeds batch supply limit");
    require(totalMinted + quantity <= TOTAL_SUPPLY, "Exceeds batch supply limit");
    for (uint i = 0; i < quantity; i++) {
        _mintSingleNFT(msg.sender,tokenUri[i],genes[i]);
    }
    mintedBatches += 1;
} else {
    // Release-based minting logic
    // require(totalReleases <= 5, "Exceeds total releases");
    require(totalMinted + quantity <= TOTAL_SUPPLY, "Exceeds total supply");
    require(quantity > 0 && quantity <= 10, "Invalid release size");
    for (uint i = 0; i < quantity; i++) {
        _mintSingleNFT(msg.sender,tokenUri[i],genes[i]);
    }
    totalReleases += 1;
    releaseSizes[totalReleases] = quantity;
}
```
