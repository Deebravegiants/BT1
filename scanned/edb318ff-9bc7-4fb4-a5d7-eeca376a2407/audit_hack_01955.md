# [C] 6.1 LPYCRV Outputs Not Transferred to User

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Critical Version 1 Code Corrected

In the zap function of ZapYCRV, converting to LPYCRV as _output_token will not transfer LPYCRV to
the user but leave it in the ZapYCRV contract instead.

When LPYCRV is the output token, ZapYCRV should first deposit YCRV as liquidity in the POOL
StableSwap pool, receiving the POOL liquidity token. The POOL liquidity token should then be deposited in
the LPYCRV vault and the issued shares transferred to the user.

The following line of code in _convert_to_output is responsible for the specified logic.

```
amount_out: uint256 = Vault(LPYCRV).deposit(self._lp([0, amount], _min_out,
_recipient))
```
which calls the self._lp(...) function, defined as

```
@internal def _lp(_amounts: uint256[2], _min_out: uint256, _recipient:
address) -> uint256:
return Curve(POOL).add_liquidity(_amounts, _min_out)
```
The _recipient argument is passed to the _lp function, but never used. The _lp function doesn't
actually need the _recipient argument, because ZapYCRV will still need to deposit the liquidity token
into the LPYCRV vault.

The Vault(LPYCRV).deposit function is called without specifying the recipient argument, which
therefore defaults to msg.sender, which is the ZapYCRV contract in the context of the deposit call.
Finally the zap function returns and the issued shares of LPYCRV are never transferred to the user, but
left to ZapYCRV instead.


Code corrected

The recipient argument of the _lp function has been removed.

```
@internal def _lp(_amounts: uint256[2]) -> uint256:
return Curve(POOL).add_liquidity(_amounts, 0)
```
A recipient value is now specified in the deposit call to the LPYCRV vault in the
_convert_to_output function.

```
amount_out: uint256 = Vault(LPYCRV).deposit(self._lp([0, amount]), _recipient)
```
