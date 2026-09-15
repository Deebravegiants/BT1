# [M] 5.2.1 _domainSeparatorV4()not updated aftername/symbolchange

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Medium Risk
**Context:** BridgeToken.sol#L58-L63, OZERC20.sol#L382-L388, OZERC20.sol#L348-L369, draft-EIP712.sol,
EIP712.sol#L69-L75, EIP712.sol#L100-L
**Description:** TheBridgeTokenallows updating thenameandsymbolof a token. However the_CACHED_DOMAIN_-
SEPARATOR(of EIP712) isn't updated. This means thatpermit(), which uses_hashTypedDataV4()and_CACHED_-
DOMAIN_SEPARATOR, still uses the old value. On the other handDOMAIN_SEPARATOR()is updated.
Both and especially their combination can give unexpected results.
BridgeToken.sol
function setDetails(string calldata _newName, string calldata _newSymbol) external override onlyOwner {
// careful with naming convention change here
token.name = _newName;
token.symbol = _newSymbol;
emit UpdateDetails(_newName, _newSymbol);
}

OZERC20.sol


```
function DOMAIN_SEPARATOR() external view override returns (bytes32) {
// See {EIP712._buildDomainSeparator}
return
keccak256(
abi.encode(_TYPE_HASH, keccak256(abi.encode(token.name)), _HASHED_VERSION, block.chainid,
,! address(this))
);
}
function permit(...) ... {
bytes32 _hash = _hashTypedDataV4(_structHash);
}
```
draft-EIP712.sol
import "./EIP712.sol";

EIP712.sol
function _hashTypedDataV4(bytes32 structHash) internal view virtual returns (bytes32) {
return ECDSA.toTypedDataHash(_domainSeparatorV4(), structHash);
}
function _domainSeparatorV4() internal view returns (bytes32) {
if (address(this) == _CACHED_THIS && block.chainid == _CACHED_CHAIN_ID) {
return _CACHED_DOMAIN_SEPARATOR;
} else {
return _buildDomainSeparator(_TYPE_HASH, _HASHED_NAME, _HASHED_VERSION);
}
}

**Recommendation:** Make the implementation ofDOMAIN_SEPARATOR()and_domainSeparatorV4()the same.
Decide on using cached versions of the domain separator. See also issue "EIP712 domain separator can be
cached"
**Connext:** Solved in PR 2350.
**Spearbit:** Verified.
