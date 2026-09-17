# [M] Unhandled return value of transferFrom in swaprouter.sol:swap can cause unwanted behavior

## Summary
Severity: Medium
Reporter: Avci
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L60-L74
Type: audit-issue

## Details
# Unhandled return value of transferFrom in swaprouter.sol:swap can cause unwanted behavior

## Summary
Unhandled return value of transferFrom in swaprouter.sol:swap can cause unwanted behavior 
## Vulnerability Detail
in the contract `swaprouter.sol` you used transferfrom but there are no checks nor any logic that handles return value of status of transferfrom
## Impact
ERC20 implementations are not always consistent. Some implementations of transfer and transferFrom could return ‘false’ on failure instead of reverting. It is safer to wrap such calls into require() statements or use safe wrapper functions implementing return value/data checks to handle these failures. especially in SWAP function 
## Code Snippet
```vyper
@external
def swap(
    _token_in: address,
    _token_out: address,
    _amount_in: uint256,
    _min_amount_out: uint256,
) -> uint256:
    ERC20(_token_in).transferFrom(msg.sender, self, _amount_in)
    ERC20(_token_in).approve(UNISWAP_ROUTER, _amount_in)

    if self.direct_route[_token_in][_token_out] != 0:
        return self._direct_swap(_token_in, _token_out, _amount_in, _min_amount_out)
    else:
        return self._multi_hop_swap(_token_in, _token_out, _amount_in, _min_amount_out)

```

https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/margin-dex/SwapRouter.vy#L60-L74


## Tool used

Manual Review

## Recommendation
- consider implementing safetransfer in vyper as you used in other parts 
```vyper

@internal
def _safe_transfer(_token: address, _to: address, _amount: uint256) -> bool:
    res: Bytes[32] = raw_call(
        _token,
        concat(
            method_id("transfer(address,uint256)"),
            convert(_to, bytes32),
            convert(_amount, bytes32),
        ),
        max_outsize=32,
    )
    if len(res) > 0:
        assert convert(res, bool), "transfer failed"

    return True

```
