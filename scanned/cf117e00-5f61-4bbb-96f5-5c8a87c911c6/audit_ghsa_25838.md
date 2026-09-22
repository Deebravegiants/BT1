# [H] Account compromise in Evmos

## Summary
Severity: High
Advisory: GHSA-5jgq-x857-p8xw
CVE: CVE-2022-24738
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-03-07
Source: https://github.com/advisories/GHSA-5jgq-x857-p8xw
Type: github-advisory

## Affected
- Go: `github.com/tharsis/evmos` — affected >=0 <2.0.1

## Details
## Impact
_What kind of vulnerability is it? Who is impacted?_

### Classification

The vulnerability has been classified as `critical` with a score of `9.0` (highest). It has the potential to affect and drain unclaimed airdrop funds from Cosmos and Osmosis eligible user addresses.

### Disclosure

The attack requires advanced knowledge of the internals of the core and application packages of IBC, IBC relayers, the Cosmos SDK `AnteHandler`,  and the Evmos `x/claims` module. The step-by-step attack is described below:

1. An actor creates a malicious chain with a custom `AnteHandler` that skips signature verification for transactions, specifically IBC `MsgTransfer`. This allows the attacker to impersonate any account by setting a custom `sender` address field of the IBC transfer message.
2.  The malicious actor then connects this newly created chain via IBC to Evmos and fills the `recipient` address from the transfer message with an address they control.
3. Once the IBC packet containing the Transfer data is relayed to Evmos, it is processed by the claims module IBC middleware. Which migrates the claim records to the recipient address, which is owned by the attacker.
4. The attacker then performs two airdrop Actions, claiming up to 75% of the total initial claimable amount.
5. The Actor repeats steps 1., 2., and 3. for every address that has unclaimed funds from the airdrop. This automatically claims 75% of the unclaimable amount.
6. The malicious actor performs the final Action, claiming 100% of all the user funds.
7. Then, the attacker transfers the funds to another chain with a DEX (Osmosis, Cosmos Hub) via IBC. 
8. Finally, the attacker withdraws the total amount in fiat through a centralized exchange. 

### Users impacted

No users have suffered the loss of funds as no malicious chains have been connected to Evmos.

## Patches
_Has the problem been patched? What versions should users upgrade to?_

The patch involves defining a list of authorized channels for chains that are connected to Evmos via IBC. This restricts the chains that have the capability of migrating users' claims records as per the specification. By default, the authorized destination channels are `"channel-0"` (Osmosis) and `"channel-3"` (Cosmos Hub).

Please upgrade your mainnet node and validator to [`v2.0.1`](https://github.com/tharsis/evmos/releases/tag/v2.0.1) **ASAP**.

## Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

No, the fix for the critical vulnerability is state machine breaking. An upgrade procedure must be coordinated with the nodes running the network.

## References

_Are there any links users can visit to find out more?_

* Claims module spec: [evmos.dev/modules/claims](https://evmos.dev/modules/claims)
* Cosmos SDK documentation: [docs.cosmos.network](https://docs.cosmos.network/)
* IBC documentation: [ibc.cosmos.network](https://ibc.cosmos.network/)

## For more information

If you have any questions or comments about this advisory:

* Reach out to the Core Team in [Discord](https://discord.gg/evmos)
* Open an issue in [tharsis/evmos](http://github.com/tharsis/evmos/issues)
* Email us at [security@thars.is](security@thars.is)

Thanks to the Core IBC team at Interchain GmbH for the secure disclosure of this vulnerability

## References
- https://github.com/tharsis/evmos/security/advisories/GHSA-5jgq-x857-p8xw
- https://nvd.nist.gov/vuln/detail/CVE-2022-24738
- https://github.com/tharsis/evmos/commit/28870258d4ee9f1b8aeef5eba891681f89348f71
- https://github.com/tharsis/evmos
- https://github.com/tharsis/evmos/releases/tag/v2.0.1
