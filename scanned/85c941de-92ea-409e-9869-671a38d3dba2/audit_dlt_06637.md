# [?] Inbound Asset Handling Incompatibility Causing Execution Reversion in ERC4626 Flow

## Summary
Severity: Unknown
Chain: Smart contract
Component: Euro-Dollar
Published: 2026-07-23
Source: https://github.com/hats-finance/Euro-Dollar-0xa4ccd3b6daa763f729ad59eae75f9cbff7baf2cd/issues/134
Type: hats-finding

## Details
### Analysis of the Vulnerability
The asset processing workflow inside the InvestToken smart contract relies on an atypical design pattern for its ERC4626 vault implementation. During fund ingestion via deposit() and mint(), the execution model triggers an external call to usde.burn(msg.sender, assets).

From a smart contract architecture perspective on the EVM, an external wrapper contract cannot perform a direct burn operation on balances held by an arbitrary user wallet. This action requires specialized mint/burn roles within the underlying USDE token system, which public participants do not possess. Consequently, standard user transactions will encounter an access violation and revert, causing a total breakdown of the system's primary funding channel.

### Exploit Vector Simulation
1. An endpoint user attempts to fund the vault by executing deposit().
2. The routine calls out to the external dependency: usde.burn(msg.sender, assets).
3. The core USDE contract stops the execution because the caller lacks the administrative clearance required to burn user-owned balances.
4. The system state reverts, blocking all capital inflows.

### Remediation Path
Reconfigure the deposit and mint routines to pull liquidity into the contract balance via transfer From prior to adjusting internal vault state metrics:

usde.transferFrom(msg.sender, address(this), assets);
