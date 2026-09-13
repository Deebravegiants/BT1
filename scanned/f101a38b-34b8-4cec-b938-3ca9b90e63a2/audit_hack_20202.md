# [H] 5.2.3 Routers can sybil attack the sponsor vault to drain funds

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** BridgeFacet.sol#L652-L
**Description:** When funds are bridged from source to destination chain messages must first go through optimistic
verification before being executed on the destinationBridgeFacet.solcontract. Upon transfer processing the
contract checks if the domain is sponsored. If such is the case then the user is reimbursed for both liquidity fees
paid when the transfer was initiated and for the fees paid to the relayer during message propagation.
There currently isn’t any mechanism to detect sybil attacks. Therefore, a router can perform several large value
transfers in an effort to drain the sponsor vault of its funds. Because liquidity fees are paid to the router by a user
connected to the router, there isn’t any value lost in this type of attack.
**Recommendation:** Consider re-thinking the sponsor vault design or it may be safer to have it removed altogether.
**Connext:** Cap implemented in PR 1631. There is no total mitigation of sybil attacks on the vault possible, and this
should be clearly explained to anyone who decides to deploy and fund one.
**Spearbit:** Verified and acknowledged.
