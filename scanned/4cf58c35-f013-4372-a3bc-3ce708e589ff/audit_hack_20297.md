# [H] 5.1.4 A maliciousowneror user with aRole.Routerrole can drain arouter's liquidity

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:**

- RoutersFacet.sol#L263-L
- RoutersFacet.sol#L
- RoutersFacet.sol#L
- BridgeFacet.sol#L
**Description:** A maliciousowneror user withRole.Router Roledenominated asAin this example, can drain a
router's liquidity for a currentrouter(arouterthat has already been added to the system and might potentially
have added big liquidities to some assets).
Here is howAcan do it (can also be done atomically):
1. Remove therouterby callingremoveRouter.
2. Add therouterback by callingsetupRouterand set theownerandrecipientparameters to accountsA
has access to / control over.
3. Loop over all tokens that therouterhas liquidity and callremoveRouterLiquidityForto drain/redirect the
funds into accountsAhas control over.
That means allrouterswould need to put their trust in theowner(of thisconnextinstance) and anyuserwho has
aRole.Router Rolewith their liquidity. So the setup is not trustless currently.
**Recommendation:** To remove this trust assumption a redesign is required for howrouters get integrated into this
system. And it starts from here, it would be best to have the function in a form likefunction addRouter(IRouter


router)(renamedsetupRoutertoaddRouter). WhereIRouteris an interface that tries to shape some require-
ments that therouterwould need to have. Arouter:

1. Needs to be able to set its ownownerorrecipientif required. It might not always be required.
2. Needs to be able to sign transfers and bid for those transfers to a sequencer.
3. If approved for using Aave Portal, it might need to be able to callrepayAavePortal. But it is not necessary
    since anyone can callrepayAavePortalForto repay the fees/debts for thisrouter.
4. Can implement calling toaddRouterLiquidityto add liquidity. But it is not necessary since anyone can call
    addRouterLiquidityForfor thisrouter.
5. If therouterdoes not register an account as itsowner(also needs to be implemented in this contract for this
    new redesign) it needs to implement callingremoveRouterLiquidityto remove its liquidity. If it does register
    anowner, implementing calls toremoveRouterLiquidityis not necessary since therouter'sownercan call
    removeRouterLiquidityFor.
**Connext:** Solved in PR 2413.
**Spearbit:** Verified.
