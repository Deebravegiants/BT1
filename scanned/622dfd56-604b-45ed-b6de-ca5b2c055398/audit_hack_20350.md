# [M] 5.1.2 Governance can backdoor new Safes via malicious upgrade

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk

**Context:** AddressProvider#L77-L90, SafeDeployer#L223-L

**Description:** TheSafeDeployercontract is responsible for deploying and configuring new "top-level" console
accounts and sub-accounts. These are initialized via the authorized safe factory address with the authorized
reference singleton (the implementation contract for Safe multi-signature wallets). These addresses upon which
theSafeDeployerrelies can be set by thegovernanceaddress of theAddressProvider.

Malicious governance could manipulate these addresses to have new accounts be deployed with an invalid, faulty
or even backdoored safe, meaning users could start unsuspectingly using their accounts and one day unsuspect-
ingly be exploited by a backdoor that governance previously installed. This could be obfuscated by making the
malicious configuration part of a sandwich attack whereby deploying transactions are wrapped with 2 transactions
that set and unset the malicious variants, this would prevent users from detecting this by simply querying and
verifying the address configured in theAddressProvider.

The likelihood for this happening is low, but if it would happen the impact for the users is high. Therefore we've set
this to medium risk.

**Recommendation:** This should be fixed by either hardcoding the safe factory and singleton addresses into the
SafeDeployercontract or allowing users to pass them in as parameters, avoiding the provider as the core source
of truth. This not only solves this issue but will also improve the gas usage of the safe creation method as
the addresses will be available locally (either via calldata parameter or hardcoded as a constant) meaning the
expensive external call + storage access will be avoided.

**Brahma:** Acknowledged, within the trust scope of governance. Need singleton to be upgradable in case new bugs
are discovered. Also severity for governance abuse and impact should be on low likelihood.

**Spearbit:** Acknowledged.
