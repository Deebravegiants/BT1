# [C] 6.1 Unprotected Escrow Funds

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Security Critical Version 1 Code Corrected

L1DAIBridge.deposit() transfers DAI from a user-specified address from to the L1Escrow contract
to lock DAI on layer one. However, a malicious user could specify from to be the L1Escrow contract
that holds all of the locked funds. The call to DAI.transferFrom() will succeed since the escrow must
have had approved the bridge contract. Ultimately, unbacked DAI could be minted on L2 and funds from
the escrow could be stolen.

Consider the following scenario:

```
1.User calls deposit() with from being the escrow contract.
```
```
2.The self-transfer from and to escrow succeeds as long as
amount <= allowance[escrow][bridge].
3.The ceiling check passes as long as balanceOf(escrow) <= ceiling since the balance does
not change.
4.Ultimately, a message to L2 is sent and unbacked DAI on L2 is minted.
```
```
5.Repeat the process.
6.Withdraw DAI from L2 to L1, such that the escrow is emptied.
```

The README.md file in the repository states:

```
### Initial configuration
```
```
... Unlimited allowance on `L1Escrow` should be given to `L1DAIBridge`.
```
Hence an attacker may drain all DAI out of the escrow.

Furthermore, e.g. by frontrunning a deposit transaction or exploiting an unlimited approval given by the
user to the bridge it is possible to steal L1 DAI from users. Consider the following scenario:

```
1.User A intends to deposit DAI to L2 and approves the bridge contract. He either gives an exact
approval for the amount he wants to deposit or may give an unlimited approval as he trusts the
bridge contract and intends to use it in the future. Next he crafts a transaction to deposit.
2.User B calls deposit() and specifies the from address to be user A. The call succeeds and B
receives funds on L2. Note that the DAI locked on L1 are from user A. This transaction frontruns the
deposit call coming from user A.
3.User A's deposit is executed but fails due to lack of allowance.
```
Note that although they are known to be potentially dangerous it is quiet common that users give infinite
approval to such systems they trust and intend to interact with frequently.

Code corrected:

The from parameter has been removed from function deposit. The DAI amount is now transferred
from msg.sender to the escrow. Hence the issue described above no longer exists.
