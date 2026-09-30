# [M] 6.6 Relay Parameter Mismatch

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Correctness Medium Version 1 Code Corrected

The L1GovernanceRelay is used to send messages to the L2 GovernanceRelay to execute spells.
However, the parameters sent by the L1 contract and the parameters the L2 contract receives do not
match. Ultimately, governance spells cannot be relayed to L2.

More specifically, the L1GovernanceRelay sends a message to L2 as follows:

```
uint256[] memory payload = new uint256[](2);
payload[0] = to;
payload[1] = selector;
```
```
StarkNetLike(starkNet).sendMessageToL2(l2GovernanceRelay, RELAY_SELECTOR, payload);
```
However, the L2 side of the governance relay consumes the message as follows:

```
@l1_handler
func relay{
syscall_ptr : felt*,
pedersen_ptr : HashBuiltin*,
range_check_ptr
}(
from_address : felt,
target : felt
):
let (l1_governance_relay) = _l1_governance_relay.read()
assert l1_governance_relay = from_address
let (calldata : felt*) = alloc()
delegate_call(target, EXECUTE_SELECTOR, 0, calldata)
```
```
return ()
end
```
The arguments of the L1 handler should consist of the from_address and payload. However, the
payload created on L1 has two elements. That ultimately lets the execution of a governance spell fail.


Code corrected:

The unused selector was removed from the payload, the payload now contains the spell only.
