# [M] Proper Use of Borrow Rate in OpenSkyPool::borrow()

## Summary
Severity: Medium
Contest weight: 0.4593
Dataset id: 12630
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
As mentioned earlier, OpenSky is a decentralized peer-to-pool pawnshop where NFT holders can borrow using their NFT assets as collateral and DeFi users can earn passive income. While examining the current borrow-related logic, we notice the current use of the borrow rate needs to be revisited. To elaborate, we show below the related borrow() function. As the name indicates, this function allows an NFT holder to borrow with the holding NFT assets as collateral. It comes to our attention that the borrow rate is computed by making use of the utilization rate before the borrow operation occurs. In fact, the proper borrow rate needs to be computed with the utilization rate after the borrow operation occurs! In other words, the current implementation may incur less cost for the borrowing user at the cost of collecting less fee for existing liquidity providers!
```solidity
function borrow(
    uint256 reserveId,
    uint256 amount,
    uint256 duration,
    address nftAddress,
    uint256 tokenId,
    address onBehalfOf
) public
    virtual
    override
    whenNotPaused
    nonReentrant
    checkReserveExists(reserveId)
    returns (uint256)
{
    require(
        duration >= SETTINGS.minBorrowDuration() &&
        duration <= SETTINGS.maxBorrowDuration(),
        Errors.BORROW_DURATION_NOT_ALLOWED
    );
    BorrowLocalParams memory vars;
    vars.borrowLimit = getBorrowLimitByOracle(reserveId, nftAddress, tokenId);
    vars.availableLiquidity = getAvailableLiquidity(reserveId);
    vars.amountToBorrow = amount;
    if (amount == type(uint256).max) {
        vars.amountToBorrow = (
            vars.borrowLimit < vars.availableLiquidity ? vars.borrowLimit : vars.availableLiquidity
        );
    }
    require(vars.borrowLimit >= vars.amountToBorrow, Errors.BORROW_AMOUNT_EXCEED_BORROW_LIMIT);
    require(vars.availableLiquidity >= vars.amountToBorrow, Errors.RESERVE_LIQUIDITY_INSUFFICIENT);
    IERC721(nftAddress).safeTransferFrom(_msgSender(), SETTINGS.loanAddress(), tokenId);
    vars.borrowRate = reserves[reserveId].getBorrowRate();
    (uint256 loanId, DataTypes.LoanData memory loan) = IOpenSkyLoan(SETTINGS.loanAddress()).mint(
        reserveId,
        onBehalfOf,
        nftAddress,
        tokenId,
        vars.amountToBorrow,
        duration,
        vars.borrowRate
    );
    reserves[reserveId].borrow(loan);
    emit Borrow(
        reserveId,
        _msgSender(),
        onBehalfOf,
        nftAddress,
        tokenId,
        vars.amountToBorrow,
        duration,
        vars.borrowRate,
        loan.borrowOverdueTime,
        loanId
    );
    return loanId;
}
```

## Recommendation
Properly revise the borrow() logic to compute the right borrow rate.
