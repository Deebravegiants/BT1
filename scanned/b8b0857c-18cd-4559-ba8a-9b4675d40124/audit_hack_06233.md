# [M] New investors claims may lead to reverts

## Summary
Severity: Medium
Reporter: Tricko
Source: https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L408-L419
Type: audit-issue

## Details
# New investors claims may lead to reverts



## Summary
New investors are able to claim WETH withdrawn before their registration, possibly leading to reverting claims.

## Vulnerability Detail
An investor who gets registered at time X is able to claim funds withdraw before X. It is not clear from the README if this is intentional. These funds withdrawn are released collateral, due to the self-repaying property of Alchemix loans, therefore from a theoretical standpoint, it does not makes sense for these funds to get payments from before their deposit time.

But also, on a pratical level, this can lead to states where claims becomes impossible for one or more investors. For ease of explanation, consider that `withdraw_underlying_to_claim` is called on regular intervals (let's call them epochs), each epoch the vault receives 1WETH per share to be redistributed. Initially, Alice is the sole investor registered and she has `10**18` shares.
    1. 1° epoch: `amount_claimable_per_share` = 1.0, vault's WETH balance = `10**18`
    2. Alice claims `10**18` WETH
    3. 2° epoch: `amount_claimable_per_share` = 2.0, vault's WETH balance = `10**18`
    4. Alice claims `10**18` WETH
    5. Bob gets registered with `10**18` shares.
    6. 3° epoch: `amount_claimable_per_share` = 3.0, vault's WETH balance = `2*10**18`
    7. Alice claims `10**18` WETH
    8. Bob tries to claim `3*10**18` WETH, but transaction reverts due to lack of funds in the vault contract.
In this scenario, unless extra WETH is added to the vault, Bob will never be able to claim because his claimable amount will always be bigger than `ERC20(WETH).balanceOf(self)`. See the proof of concept for this scenario on the POC section below.

On a general case, in a vault with dozens of investors registred, there are three possible outcomes:
    - If Bob manages to claim faster than others investors, one or more investors (depending on how much Bob claimable amount was) won't be able to claim.
    - If Bob tries to claim later than the others, he will not be able to claim.
    - If the contract has sufficient extra balance (more than what is due to `withdraw_underlying_to_claim`). Bob will be able to claim, but will incur permanent loss of funds to the contract.

## Impact
As explained above, depending on the exact circumstances, one or more user won't be able to claim or contract's funds will be permanently loss.

## Proof of Concept

Run the following test with pytest
```python
import pytest

import boa

def test_POC(vault, owner, alice, bob, nft, weth):
    nft.DEBUG_transferMinter(owner)
    nft.mint(alice, 0)
    vault.eval(
        f"self.positions[0] = Position({{token_id: {0}, amount_deposited: {1*10**18}, amount_claimed: 0, shares_owned: {1*10**18}, is_liquidated: False}})"
    )
    vault.eval(f"self.amount_claimable_per_share = 0")

    ## First epoch
    weth.transfer(vault, 1*10**18)
    vault.eval(f"self.total_shares = {1*10**18}")
    vault.eval(f"self._mark_as_claimable({1*10**18})")
    amount = vault.claimable_for_token(0)
    assert amount == 10**18 
    balance_before = weth.balanceOf(alice)
    with boa.env.prank(alice):
        vault.claim(0) ## Alice claims 10**18 successfully
    balance_after = weth.balanceOf(alice)
    assert balance_after == balance_before + amount

    ## Second epoch
    weth.transfer(vault, 1*10**18)
    vault.eval(f"self._mark_as_claimable({1*10**18})")
    amount = vault.claimable_for_token(0)
    assert amount == 10**18
    balance_before = weth.balanceOf(alice)
    with boa.env.prank(alice):
        vault.claim(0) ## Alice claims 10**18 successfully
    balance_after = weth.balanceOf(alice)
    assert balance_after == balance_before + amount

    ## Bob gets registered
    nft.mint(bob, 1)
    vault.eval(
        f"self.positions[1] = Position({{token_id: {1}, amount_deposited: {1*10**18}, amount_claimed: 0, shares_owned: {1*10**18}, is_liquidated: False}})"
    )

    ## Third epoch
    weth.transfer(vault, 2*10**18)
    vault.eval(f"self.total_shares = {2*10**18}")
    vault.eval(f"self._mark_as_claimable({2*10**18})")
    amount = vault.claimable_for_token(0)
    assert amount == 10**18 
    balance_before = weth.balanceOf(alice)
    with boa.env.prank(alice):
        vault.claim(0) ## Alice claims 10**18 successfully
    balance_after = weth.balanceOf(alice)
    assert balance_after == balance_before + amount

    assert weth.balanceOf(vault) == 10**18

    amount = vault.claimable_for_token(1)
    assert amount == 3*10**18  
    with boa.env.prank(bob):
        with boa.reverts():
            ## Bob tries to claims 3*10**18 and reverts due to lack of funds
            vault.claim(1) 
```
## Code Snippet
https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L408-L419

https://github.com/sherlock-audit/2023-02-fair-funding/blob/main/fair-funding/contracts/Vault.vy#L443-L462

## Tool used
Manual Review

## Recommendation
During registration consider storing `amount_claimable_per_share` at that time in the `Position` struct, so it can be subtracted from future `claimable_for_token` calculations.
