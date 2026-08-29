# [M] raw_call with outsize=0 and revert_on_failure=False returns incorrect success value

## Summary
Severity: Medium
Chain: Vyper
Component: vyperlang/vyper
CVE: CVE-2023-30629
Published: 2023-04-24
Source: https://github.com/vyperlang/vyper/security/advisories/GHSA-w9g2-3w7p-72g9
Type: github-advisory

## Details
### Background
During the audit of [Lido's Gate Seals](https://github.com/lidofinance/gate-seals) code [statemind](https://statemind.io) team identified a weird behavior of the code that uses `raw_call`: https://github.com/lidofinance/gate-seals/blob/051593e74df01a4131c485b4fda52e691cd4b7d8/contracts/GateSeal.vy#L164 .

Construction like this:
```vyper
success = raw_call(
    sealable,
    _abi_encode(SEAL_DURATION_SECONDS, method_id=method_id("pauseFor(uint256)")),
    revert_on_failure=False
)
```
was not fully documented: https://docs.vyperlang.org/en/v0.3.7/built-in-functions.html#raw_call .

The documentation says that: if `max_outsize=0` it should return nothing and then it says that if `revert_on_failure=False` it should return a `success` flag in the tuple of response, but what if `max_outsize=0`  and `revert_on_failure=False`.

<img width="715" alt="image" src="https://user-images.githubusercontent.com/22330612/232125364-d2b3bbac-0b4f-40cb-80ff-f55d8eafef44.png">

 So the team started researching what exactly happened in that case, after some research we found that the Vyper compiler generates the wrong bytecode in that case, it generates the sequence:
```
CALL // call
MLOAD // MLOAD is wrong since the CALL result is already stored in the stack
```

### Impact
Example of buggy code:
```vyper
@external
def returnSome(calling: address, a: uint256) -> bool:
    success: bool = false
    success = raw_call(
        calling,
        _abi_encode(a, method_id=method_id("a(uint256)")),
        revert_on_failure=False
        )
```

any contract that uses the `raw_call` with `revert_on_failure=False` and `max_outsize=0` receives the wrong response from `raw_call`. Depending on the memory garbage, the result can be either `True` or `False`.


_Trimmed to 38 lines — full report: https://github.com/vyperlang/vyper/security/advisories/GHSA-w9g2-3w7p-72g9_
