# [M] Improved Sanity Checks For System/Function Parameters

## Summary
Severity: Medium
Contest weight: 0.4552
Dataset id: 12941
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```solidity
uint256 public _maxSupply = 5555;

function mint(uint256 qty) public payable virtual {
    require(!paused);
    require(msg.value >= 0, "Not enough ROSE sent; check price!");
    require(_tokenIdCounter.current() < _maxSupply);
    // Whitelist mode. We will have a whitelist event.
    if (whitelistMode) {
        if (whitelistCheck) {
            require(whitelisted[msg.sender], "Only whitelist participants are allowed during whitelist sale.");
            uint256 requiredAmount = qty * _whitelistSalePrice;
            uint256 arrayLength = userOwnedTokensWhitelist[msg.sender].length;
            uint256 toBeTotal = arrayLength + qty;
            require(toBeTotal < (_whitelistOwnershipLimit + 1), "Maximum Holding for WL Event"); // only 3 allowed!
            require(msg.value >= requiredAmount, "Not enough ROSE sent; check price!");
            // Mint for whitelist
            for (uint256 i = 1; i <= qty; i++) {
                _tokenIdCounter.increment();
                uint256 tokenId = _tokenIdCounter.current();
                userOwnedTokensWhitelist[msg.sender].push(tokenId);
                _mint(msg.sender, tokenId);
            }
        } else {
            uint256 requiredAmount = qty * _publicSalePrice;
            uint256 arrayLength = userOwnedTokensPublic[msg.sender].length;
            uint256 toBeTotal = arrayLength + qty;
            require(toBeTotal < (_publicOwnershipLimit + 1), "Maximum Holding for Public Event"); // only 15 allowed!
            require(msg.value >= requiredAmount, "Not enough ROSE sent; check price!");
            // Mint for public
            for (uint256 i = 1; i <= qty; i++) {
                _tokenIdCounter.increment();
                uint256 tokenId = _tokenIdCounter.current();
                userOwnedTokensPublic[msg.sender].push(tokenId);
                _mint(msg.sender, tokenId);
            }
        }
    }
}
```

## Recommendation
Revisit the above mentioned routine to add proper sanity checks.
