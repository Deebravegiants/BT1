# [M] Wrong Equals Logic

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-07-ens
Published: 2022-07-19
Source: https://github.com/code-423n4/2022-07-ens-findings/issues/118
Type: code-finding

## Details
# Lines of code

https://github.com/code-423n4/2022-07-ens/blob/ff6e59b9415d0ead7daf31c2ed06e86d9061ae22/contracts/dnssec-oracle/BytesUtils.sol#L115-L127


# Vulnerability details

## Impact
`equals` with offset might return true when `equals` without offset returns false.

## Proof of Concept
The problem is that `self.length` could be greater than `other.length + offset`, it should be `==`, or it should contain a length argument.

Here you have an example of the failure:

- `equals(0x0102030000, 0, 0x010203)` => `return true`

```json
decoded input	{
	"bytes self": "0x0102030000",
	"uint256 offset": "0",
	"bytes other": "0x010203"
}
decoded output	{
	"0": "bool: true"
}
```
## Recommended Mitigation Steps
```diff
    function equals(bytes memory self, uint offset, bytes memory other) internal pure returns (bool) {
-       return self.length >= offset + other.length && equals(self, offset, other, 0, other.length);
+       return self.length == offset + other.length && equals(self, offset, other, 0, other.length);
    }
```
