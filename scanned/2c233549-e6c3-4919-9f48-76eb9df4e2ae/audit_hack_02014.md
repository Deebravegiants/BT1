# [M] 6.7 Unlimited Approvals and the Range of Uint

## Summary
Severity: Medium
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
Design Medium Version 1 Code Corrected

DAI on L1 supports unlimited approvals using uint256(-1) as magic value. When an approval for this
magic value is given, the spender can spend the funds of the token holder without the allowance being
reduced.

Similarly the DAI contract in cairo supports an unlimited approval using a different magic number. As
Uint256 work differently in cairo, it's possible to define a magic value outside the actual range of Uint256.
In cairo, a Uint256 is represented by a struct containing two felt members:

```
struct Uint256:
# The low 128 bits of the value.
member low : felt
# The high 128 bits of the value.
member high : felt
end
```
However note that a felt can store more than 128 bits, so a Uint256 represented by such a struct may
contain a value exceeding the max uint256 value.

The code of the DAI cairo contract, however, takes advantage of this special property of the Uint256 type
and defines the magic number for the unlimited approval as:

```
const MAX_SPLIT = 2**
let MAX = Uint256(low=MAX_SPLIT, high=MAX_SPLIT)
```
Note that the common library for Uint256 offers a function uint256_check which checks if the given
Uint256 is actually valid. The code of the DAI cairo contract uses this function to check whether amounts
regarding balances are valid. In contrast, the code is generally not using uint256_check() when
handling or checking approvals. That results in following potentially intended and/or strange behaviour:

- Function approve can be used to give allowance for a valid amount, the magic number or an invalid
    uint256 value.
- Function increase_allowance does not work on such allowances due to the carry over.
    However, increasing with bad input values could decrease the allowance (in a similar fashion as
    described in L2 DAI allows stealing).
- Function decrease_allowance works. However, note that decreasing to the magic number
    results in unlimited approval so that allowance has been increased instead of decreased.

Concluding, the selection of the magic value outside the valid range for Uint256 could lead to unexpected
and undocumented behaviour due to an implied lack of Uint256 validity checks. Furthermore, the
deviation from L1-DAI's magic value may confuse users.

Code corrected:

MAX_SPLIT has been renamed to ALL_ONES and redefined to 2**128-1. Also, uint256_check() is
called now in the functions approve, increase_allowance and decrease_allowance. Since the
inputs are always validated and allowance cannot be out of the valid Uint256 range, the unintended
behaviour cannot occur anymore.
