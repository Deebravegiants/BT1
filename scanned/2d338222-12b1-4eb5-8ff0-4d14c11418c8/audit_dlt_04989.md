# [H] Two malicious users can drain a big amount of rewards up to 48 weeks, for the little lock time of 10 mins.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-merit-circle
Published: 2022-10-14
Source: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/36
Type: sherlock-finding

## Details
CodingNameKiki

high

# Two malicious users can drain a big amount of rewards up to 48 weeks, for the little lock time of 10 mins.

## Summary
By following the scenario in "Vulnerability Detail", two malicious users can drain rewards from the pool.

## Vulnerability Detail
Example: 
Kiki calls the function `deposit()` and locks tokens for himself, for the duration of 48 weeks and provides his address as the `_receiver`. Then he calls the function `deposit()` again and locks funds for Bob as well, for the duration of 10 mins and provides Bob's address as the `_receiver`. After that Kiki calls the function `increaseLock()` and provides his `_depositId` and Bob's address as the `_receiver`.

Since Kiki is the msg.sender calling the function `increaseLock()`, and provides his `_depositId`. 
The function will successfuly make a copy in memory from Kiki's Deposit lock with the duration of 48 weeks:

https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L203

The `remaingDuration` will be calculated based on the Kiki's lock information, which he made for the duration of 48 weeks.

https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L213

And the `mintAmount` will be calculated based on the `increaseAmount` provided by Kiki and the sum of the `remaingDuration`.

https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L215

However the problem here is that by providing Bob's address as the `_receiver`. The mapping `depositsOf` will take Bob's address and will lead to Bob's lock information. Duo to the fact that Kiki made the two deposits and the `_depositId` will be the same for the two deposits, but only the right address will lead to the right deposit information. This way the function `increaseLock()` can be tricked to add the calculated `mintAmount` based on the Kiki's 48 weeks lock to Bob's lock balance.

`If l understood right from the sponsor, the _depositId is created, when the user's wallet is connected to the site.`
`And when Kiki did the two deposits - one for him and one for Bob. The _depositId will be the same for the two deposits.` 
`Kiki's address will lead to Kiki's lock and Bob's address will lead to Bob's lock, even tho the _depositId is the same.`

The function will successfuly add the `_increaseAmount` and `mintAmount` calculated based on the Kiki's 48 weeks lock duration to Bob's lock of 10 mins.

https://github.com/sherlock-audit/2022-10-merit-circle/blob/main/merit-liquidity-mining/contracts/TimeLockPool.sol#L217-L218

When Bob's 10 mins lock duration ends, he can successfuly claim the big amount of rewards calculated based on the Kiki's 48 week duration lock. After that Bob can withdraw the `increaseAmount` provided by Kiki as well and both of them can repeat this process and successfuly drain rewards from the BasePool.


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-merit-circle-judging/issues/36_
