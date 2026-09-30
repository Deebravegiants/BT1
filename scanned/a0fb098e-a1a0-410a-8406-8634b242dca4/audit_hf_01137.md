# [H] _exchangerate can be manipulated, leading to inflation attack

## Summary
Severity: High
Reporter: 0xTheBlackPanther, also found by J4X98, Chad0, golu and Victor Okafor
Contest weight: 0.2971
Dataset id: 4817
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability consists of an exchange rate variable that can be arbitrarily set by an attacker during the deposit function of the Omnipool contract. Because the contract does not restrict who can modify the internal _exchangeRate, the attacker can call deposit with a crafted amount that forces the contract to record a manipulated rate. Once the rate is set to an extreme value, subsequent legitimate deposits calculate the amount of LP tokens based on the corrupted rate, resulting in zero or negligible LP tokens being minted for the depositor. From the user’s perspective the transaction appears successful but the UI shows no increase in LP balance, effectively making the deposit unprofitable. The attacker can then withdraw the previously supplied tokens, draining the pool while other users are unable to earn any share. The issue arises because the exchange rate is derived from external input rather than a trusted source and is not locked after initialization. It is triggered whenever a deposit is performed before a legitimate rate is established, or any time the contract permits the rate to be overwritten. The flaw was discovered during a security audit that exercised the deposit path with a malicious caller. It is difficult to notice because the contract does not emit a specific error; the only symptom is that users receive zero LP tokens despite a successful deposit. This class of bug falls under mutable pricing parameter manipulation, similar to oracle manipulation, and violates the fundamental accounting assumption that the pool’s price reflects the true market value of the underlying assets. The recommended mitigation is to initialize the exchange rate at deployment from a trusted source, make the variable immutable or only updatable by a privileged role, and to compute the rate internally on each deposit rather than accepting a caller‑controlled value. By ensuring the rate cannot be set arbitrarily, the pool preserves correct token accounting and prevents attackers from inflating or deflating the price to steal funds.

## Proof of Concept
1. Hacker Sets Exchange Rate: The attacker initiates a deposit by setting the exchangeRate during a deposit, for example: vm.startPrank(hacker); omnipool.deposit(2, 0); token.transfer(address(omnipool), 2); vm.stopPrank(); 2. Victims Attempt to Deposit: Other users (victims) try to deposit into the omnipool after the exchange rate manipulation. Due to the manipulated exchange rate, victims receive zero LP tokens for their deposits. Example: vm.startPrank(user); token.approve(address(omnipool), 10 ** 18); omnipool.deposit(10 ** 18, 0); vm.stopPrank(); 3. Attacker Withdraws All Tokens: The attacker starts to withdraws all tokens from the pool, example: vm.startPrank(hacker); omnipool.withdraw(1, 0);

## Recommendation
One of the simplest solutions is to execute a deposit immediately after the deployment of the contract. By doing so, the exchangeRate can be adjusted to a desired and controlled value, mitigating the risk of potential manipulation. Some of the recommendations along with their pros and cons, can be found in OpenZeppelin github issue 3706.
