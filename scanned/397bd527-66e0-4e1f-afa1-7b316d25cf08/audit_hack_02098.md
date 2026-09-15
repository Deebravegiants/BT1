# [M] 6.2 Sandwich Attack on New Liquidity Providers

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Medium Version 1 Code Corrected

This attack works against new liquidity providers when they are adding liquidity. The overall idea of the
attack is that the virtual reserve values are out of sync with the reserve values. Hence, the slippage
protection of addLiquidity() can be circumvented. The reserve values are brought out of sync by
adding unbalanced liquidity. Adding unbalanced liquidity by itself is good for liquidity providers, but in this
combination it can be used for an attack.

Prerequisites:

- A pool with little liquidity, e.g. new pool
- The pool is amplified
- The attacker has the ability to perform a sandwich attack

Setup:

- The pool has two token T0, T
- T0 is worth 100 USD
- T1 is worth 1 USD
- The pool is balanced, e.g. 1 T0 and 100 T

Attacks Steps:

```
1.Attacker adds liquidity regularly through the router. Hence, the pool is still correctly balanced. In
particular the reserves and virtual reserves have the ratio 1:100.
2.The victim looks at the pool and decides to add liquidity
```
- The victim uses the router and allows for no slippage or a tiny amount of slippage (hence,
    following best practices)
- The victim sets up amountADesired and amountBDesired in 1:100 ratio, also amountAMin and
    amountBMin have 1:100 ratio

```
4.The attacker detect the victim transaction in the mempool and starts a sandwich attack
5.First attacker transaction:
```
- The attacker swaps all of T0 out of the pool
- The attacker adds unbalanced liquidity (as described in our report)
- These two steps can be repeated
- As a result the reserves are in a 1:100 ratio but the virtual reserves are in a different ratio, e.g.
    1:210 in our example

```
6.The victim transaction is executed, all checks pass, the transaction is successfully completed
```

```
7.Second attacker transaction:
```
- Attacker removes all its liquidity from the pool, now only the victim's liquidity is in the pool
- Attacker uses the incorrect ratio of the virtual reserves to execute a swap that is bad for the
    victim

Effect and Analysis:

- The "gifted" liquidity through unbalanced minting here goes back to the attacker as they are the
    only/primary liquidity provider
- In our example with an amplification factor of 100, the attacker can steal 12.69% of the victim's
    funds. Hence, the more the victim deposits, the more can be stolen.
- The attacker's funds can be smaller than the victim's funds. The percentage of stolen funds remains
    the same.
- This is independent of the price ratios between T0 and T1 (1:100 in this example). Different ratios
    lead to the same outcome.
- Other amplification factors lead to different results, but there are probably ways to make this attack
    more effective

Example Numbers:

Pool after liquidity has been added:

### [++] T0: 1.

### [++] T1: 100.

```
[++] Value: 200.0 USD
[+] Value of 1 LP Share: 20.00 USD
[+] Virtual Reserves: 10.00, 1000.
```
At this point all seems fine and the victim decides to add liqudity.

Pool after pre-manipulation:

### [++] T0: 5.

### [++] T1: 552.

```
[++] Value: 1104.97 USD
[+] Value of 1 LP Share: 110.50 USD
[+] Virtual Reserves: 6.89, 1452.
```
At this point the reserves are still in a 1:100 ratio, but the virtual reserves are not. There ratio is 1:210.

Pool before final swap to exploit incorrect ratios:

### [++] T0: 100.

### [++] T1: 10000.

```
[++] Value: 20000.0 USD
[+] Value of 1 LP Share: 110.50 USD
[+] Virtual Reserves: 124.68, 26290.
```
At this point only the victim's liquidity is left. The ratio of the virtual reserves is still 1:210.

Code corrected:

The router now features a slippage protection on the ratio of the virtual reserves. The function takes two
new arguments where users can specify the lower and upper bound for the ratio between the virtual


reserves. This mitigates the attack described above as the attacker can no longer arbitrarily unbalance
the virtual reserves. Note that the protection is in the Router, hence, users interacting with the pool
contract directly are not protected.
