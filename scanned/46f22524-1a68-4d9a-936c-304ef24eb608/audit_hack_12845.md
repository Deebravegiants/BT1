# [M] Hardcoded twap oracle address does not exist in the deployment chain

## Summary
Severity: Medium
Reporter: TheNaubit
Source: https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49
Type: audit-issue

## Details
# Hardcoded twap oracle address does not exist in the deployment chain

## Summary
In the `Dca` contract there is a hardcoded (`constant`) address that contains the address of the Twap Oracle the protocol will use. The protocol is going to be deployed in Arbitrum but after checking the blockchain, that address does not contain any Twap oracle so calls to this address will always revert.

## Vulnerability Detail
The hardcoded address is `0xFa64f316e627aD8360de2476aF0dD9250018CFc5` and when checked the address in Arbiscan (since the project is going to be deployed in Arbitrum), the address does not have any Twap contract deployed: https://arbiscan.io/address/0xFa64f316e627aD8360de2476aF0dD9250018CFc5

If the current audited contracts where going to be deployed, all the functions using this Twap oracle would revert since the contract does not exist. This means the functions `_calc_min_amount_out`, `calc_min_amount_out` and `execute_dca_order` would always revert, making impossible for any user to execute their DCA orders.

## Impact
A core function in the protocol (`execute_dca_order`) won't work.

## Code Snippet
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L49
- https://github.com/sherlock-audit/2023-06-unstoppable/blob/main/unstoppable-dex-audit/contracts/spot-dex/Dca.vy#L268

## Tool used
Manual Review

## Recommendation
If the contract is not yet deployed, they should enter a comment (for example a `// TODO` comment) to remind themselves to change it later on. But even better, the protocol should implement an admin function to change the Twap Oracle address in the future, so even if they deployed the contract with the wrong address by mistake, they could change it without having to redeploy. Something like this:
```vyper
@external
def set_twap_address(_twap_address: address):
    assert msg.sender == self.owner, "unauthorized"
    assert _twap_address != empty(address), "new twap address can not be the zero address"

    # Protocol will have to change the TWAP var from a constant to a normal state var before implementing this
    twap_address = _twap_address

    log TwapAddressChanged(_twap_address)
```
