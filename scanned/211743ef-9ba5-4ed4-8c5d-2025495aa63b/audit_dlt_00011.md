# [H] Consensus flaw during block processing

## Summary
Severity: High
Chain: Ethereum
Component: ethereum/go-ethereum
CVE: CVE-2020-26265
Published: 2020-12-11
Source: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-xw37-57qp-9mm4
Type: github-advisory

## Details
### Impact

A consensus-vulnerability in Geth could cause a chain split, where vulnerable versions refuse to accept the canonical chain. 

### Description


A flaw was repoted at 2020-08-11 by John Youngseok Yang (Software Platform Lab), where a particular sequence of transactions could cause a consensus failure.

- Tx 1:
  - `sender` invokes `caller`.
  - `caller` invokes `0xaa`. `0xaa` has 3 wei, does a self-destruct-to-self
  - `caller` does a  `1 wei` -call to `0xaa`, who thereby has 1 wei (the code in `0xaa` still executed, since the tx is still ongoing, but doesn't redo the selfdestruct, it takes a different path if callvalue is non-zero)

- Tx 2:
  - `sender` does a 5-wei call to 0xaa. No exec (since no code). 

In geth, the result would be that `0xaa` had `6 wei`, whereas OE reported (correctly) `5` wei. Furthermore, in geth, if the second tx was not executed, the `0xaa` would be destructed, resulting in `0 wei`. Thus obviously wrong. 

It was determined that the root cause was this [commit](https://github.com/ethereum/go-ethereum/commit/223b950944f494a5b4e0957fd9f92c48b09037ad) from [this PR](https://github.com/ethereum/go-ethereum/pull/19953). The semantics of `createObject` was subtly changd, into returning a non-nil object (with `deleted=true`) where it previously did not if the account had been destructed. This return value caused the new object to inherit the old `balance`:

```golang
func (s *StateDB) CreateAccount(addr common.Address) {
	newObj, prev := s.createObject(addr)
	if prev != nil {
		newObj.setBalance(prev.data.Balance)
	}
}
```

It was determined that the minimal possible correct fix was

```diff
+++ b/core/state/statedb.go
@@ -589,7 +589,10 @@ func (s *StateDB) createObject(addr common.Address) (newobj, prev *stateObject)
                s.journal.append(resetObjectChange{prev: prev, prevdestruct: prevdestruct})
        }
        s.setStateObject(newobj)
```

_Trimmed to 38 lines — full report: https://github.com/ethereum/go-ethereum/security/advisories/GHSA-xw37-57qp-9mm4_
