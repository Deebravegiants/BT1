# [H] 5.2.13 Tokens can get stuck inExecutorcontract if thedestinationdoesn’t claim them all

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** High Risk
**Context:** Executor.sol#L142-L
**Description:** The functionexecute()increases allowance and then calls the recipient (_args.to). When the
recipient does not use all tokens, these could remain stuck inside theExecutorcontract.
Note: theexecutorcan have excess tokens, see: kovan executor. Note: see issue "Malicious call data can DOS
executeor steal unclaimed tokens in theExecutorcontract".
function execute(...) ... {
if (!isNative && hasValue) {
SafeERC20.safeIncreaseAllowance(IERC20(_args.assetId), _args.to, _args.amount);
}
(success, returnData) = ExcessivelySafeCall.excessivelySafeCall( _args.to, ... );
}

**Recommendation:** Determine what should happen with unclaimed tokens. Consider one or more of the following
suggestions:

- Send the unclaimed tokens to the recovery address via_sendToRecovery()(although this further compli-
    cates the contract).
- Set theallowanceto 0 (beforesafeIncreaseAllowance()or after the call toexcessivelySafeCall()).
- Allow the retrieval of unclaimed tokens from theexecutorcontract by an owner.
**Connext:** New policy: "any funds left in the Executor following a transfer are claimable by anyone". This forces
implementers to think carefully about the calldata. Thus leave the issues as is.
**Spearbit:** Acknowledged.
Note: as it requires some deliberate action to retrieve the tokens, in practice several tokens will stay behind in the
executor.
