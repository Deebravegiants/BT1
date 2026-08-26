# [M] ecrecover can return undefined data for invalid signatures

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-37902
Published: 2023-07-25
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-f5x6-7qgp-jhf3
Type: github-advisory

## Details
### Impact
the ecrecover precompile does not fill the output buffer if the signature does not verify, see https://github.com/ethereum/go-ethereum/blob/b058cf454b3bdc7e770e2b3cec83a0bcb48f55ee/core/vm/contracts.go#L188. however, the ecrecover builtin will still return whatever is at memory location 0.

this means that the if the compiler has been convinced to write to the 0 memory location with specially crafted data (generally, this can happen with a hashmap access or immutable read) just before the ecrecover, a signature check might pass on an invalid signature.

A contract search was performed. Most uses of `ecrecover` are used for erc2612-style permit implementations, which typically look like:

```vyper
    assert _owner != empty(address)
    assert block.timestamp <= _deadline
                  
    nonce: uint256 = self.nonces[_owner]
    digest: bytes32 = keccak256(
        concat(   
            b"\x19\x01",
            self.DOMAIN_SEPARATOR,
            keccak256(_abi_encode(PERMIT_TYPEHASH, _owner, _spender, _value, nonce, _deadline))
        )         
    )             
    assert ecrecover(digest, convert(_v, uint256), convert(_r, uint256), convert(_s, uint256)) == _owner
```

in this case, the immutable `PERMIT_TYPEHASH` is loaded into `ecrecover`'s output buffer right before `ecrecover()`, and so the output of `ecrecover()` here when the signature is invalid will be the value of `PERMIT_TYPEHASH`. in this case, since `PERMIT_TYPEHASH` is not a valid address, it will never compare `==` to `_owner`, and so the behaviour is exactly the same as if `ecrecover()` returned 0 in this case.

in general, a contract could have unexpected behavior (i.e. mistakenly pass this style of signature check) if an immutable representing a real address (ex. `OWNER`) was read right before the `ecrecover` operation.

### Patches
v0.3.10 (with 019a37ab98ff53f04fecfadf602b6cd5ac748f7f and #3586)

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References
_Are there any links users can visit to find out more?_
