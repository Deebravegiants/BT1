# [M] Multichain incident: Multichain's AnyswapV4Router contract suffered a rush attack, and the attacker made a profit of about 87 Ethereum, about $130,000

## Summary
Severity: Medium
Target: Multichain
Loss: $ 130,000
Attack method: Rush Attack
Published: 2023-02-15
Source: https://www.panewslab.com/zh/sqarticledetails/543vc392.html
Type: slowmist-incident

## Details
Multichain's AnyswapV4Router contract suffered a rush attack, and the attacker made a profit of about 87 Ethereum, about $130,000. After analysis, the attacker used the MEV contract (0xd050) to pre-emptively call the anySwapOutUnderlyingWithPermit function of the AnyswapV4Router contract before the normal transaction was executed (the user authorized WETH but has not yet performed the transfer), although the function uses the permit signature of the token verification, but the stolen WETH this time does not have a relevant signature verification function, and only triggers a deposit function in a fallback. In subsequent function calls, the attacker can directly use the safeTransferFrom function to transfer the WETH authorized by the _underlying address to the attacked contract to the attack contract without signature verification.
