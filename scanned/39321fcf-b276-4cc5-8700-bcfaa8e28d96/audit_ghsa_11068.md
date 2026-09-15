# [H] @keep-network/tbtc-v2 revealing P2PKH deposit with a wrapped P2SH script

## Summary
Severity: High
Advisory: GHSA-8986-v76q-8vr2
CWE: CWE-328
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-8986-v76q-8vr2
Type: github-advisory

## Affected
- npm: `@keep-network/tbtc-v2` — affected >=0 <1.8.2

## Details
# Overview

P2PKH has 20 bytes just like P2SH. We protect against revealing P2PKH deposits by manually assembling the expected P2SH script in the smart contract and comparing hashes. However, we missed the case when the attacker embeds a valid P2SH inside of P2PKH as an output script. bitcoin-spv library [extracts the P2SH from P2PKH](https://github.com/keep-network/bitcoin-spv/blob/856849612ef49114af18c0f407eaa74afc2ee4be/solidity/contracts/BTCUtils.sol#L610-L612) and we treat it as a valid P2SH output.

This does not lead to stealing funds but can lead to protocol insolvency.

The off-chain client handles this case correctly, but the problem is in the optimistic minting bot. The bot assumes that if the funding TX exists on Bitcoin with the right amount and it was successfully revealed, the transaction is valid.

https://bugs.immunefi.com/magnus/672/projects/502/bug-bounty/reports/55982

# Steps

Since there is a 24-hour governance delay on upgrading the Bridge smart contract, we are going to pause optimistic minting.

1. Pause optimistic minting.
2. Deploy new Bridge implementation with Deposit library containing a fix, WITHOUT VERIFYING THE CODE on Etherscan.
3. Schedule upgrade transaction.
4. After 24 hours, finalize upgrade.
5. Unpause optimistic minting.

## References
- https://github.com/threshold-network/tbtc-v2/security/advisories/GHSA-8986-v76q-8vr2
- https://bugs.immunefi.com/magnus/672/projects/502/bug-bounty/reports/55982
- https://github.com/keep-network/bitcoin-spv/blob/856849612ef49114af18c0f407eaa74afc2ee4be/solidity/contracts/BTCUtils.sol#L610-L612
- https://github.com/threshold-network/tbtc-v2
