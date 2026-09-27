# [H] Exactly Protocol incident: The DeFi lending protocol Exactly Protocol was attacked and lost more than 7,160 ETH (approximately $12.04 million). The two contr

## Summary
Severity: High
Target: Exactly Protocol
Loss: $ 7,300,000
Attack method: Unchecked Input Data
Published: 2023-08-18
Source: https://www.wu-talk.com/index.php?m=content&amp;c=index&amp;a=show&amp;catid=46&amp;id=17283
Type: slowmist-incident

## Details
The DeFi lending protocol Exactly Protocol was attacked and lost more than 7,160 ETH (approximately $12.04 million). The two contract attackers attack by calling the function kick() multiple times and use the developer contract on Ethereum to transfer deposits to Optimism and eventually transfer the stolen funds back to Ethereum. The root cause of the Exactly Protocol attack is #insufficient_check, the attacker bypasses the permission check in the leverage function of the DebtManager contract by directly passing an unverified fake market address and changing _msgSender to the victim address. Then, in an untrusted external call, the attacker re-enters the crossDeleverage function in the DebtManager contract and steals the collateral from the _msgSender class. Exactly Protocol tweeted that the suspension of the agreement has been lifted, users can perform all operations, and no liquidation has occurred. The hack only affected users using the peripheral contract (DebtManager), the protocol is still functioning normally.
