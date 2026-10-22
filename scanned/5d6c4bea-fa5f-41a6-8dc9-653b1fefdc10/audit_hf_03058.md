# [M] `secondaryMinter` may break `plotsAvailablePerSize`

## Summary
Severity: Medium
Contest weight: 0.2760
Dataset id: 17250
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
RuniverseLand allows primaryMinter and secondaryMinter to mint NFT.
    
    function mintTokenId(
        address recipient,
        uint256 tokenId,
        PlotSize size
    ) public override nonReentrant {
        require(numMinted < MAX_SUPPLY, "All land has been minted");
        require(
            _msgSender() == primaryMinter || _msgSender() == secondaryMinter,
            "Not a minter"
        );
        numMinted += 1;
        emit LandMinted(recipient, tokenId, size);    
        
        _mint(recipient, tokenId);
    }

RuniverseLandMinter, as one of them, will have a limit on the number of NFTs with different PlotSize
    
    uint256[] public plotsAvailablePerSize = [
        52500, // 8x8
        16828, // 16x16
        560, // 32x32
        105, // 64x64
        7 // 128x128
    ];

This will be checked in `_mintTokens`
    
    function _mintTokens(
        IRuniverseLand.PlotSize plotSize,
        uint256 numPlots,
        address recipient
    ) private {        
        require(
            plotsMinted[uint256(plotSize)] <
                plotsAvailablePerSize[uint256(plotSize)],
            "All plots of that size minted"
        );        
        require(
            plotsMinted[uint256(plotSize)] + numPlots <=
                plotsAvailablePerSize[uint256(plotSize)],
            "Trying to mint too many plots"
        );        
        for (uint256 i = 0; i < numPlots; i++) {

            uint256 tokenId = ownerGetNextTokenId(plotSize);            
            plotsMinted[uint256(plotSize)] += 1; 

But the other minter is not limited and can mint RuniverseLand with any tokenID, thus breaking the plotsAvailablePerSize limit.

## Proof of Concept
[contracts/RuniverseLand.sol#L88-L102](https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/dcad1802bf258bf294900a08a03ca0d26d2304f4/contracts/RuniverseLand.sol#L88-L102)  
[contracts/RuniverseLandMinter.sol#L323-L341](https://github.com/code-423n4/2022-12-forgotten-runiverse/blob/dcad1802bf258bf294900a08a03ca0d26d2304f4/contracts/RuniverseLandMinter.sol#L323-L341)

## Recommendation
Consider making RuniverseLandMinter the only minter for RuniverseLand.

Risk of broken invariant, will flag, unsure about severity.

The warden has shown a way to bypass specific checks, while the function is privileged, the lack of checks is inconsistent with the checks applied in other parts of the codebase.

For this reason, I agree with Medium Severity.
