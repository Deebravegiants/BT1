# [M] EL-2022-10: SMOD consensus flaw in Nethermind

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Nethermind
Published: 2023-05-03
Source: https://notes.ethereum.org/lzl_2mBPTimS9PjkWZMW9w
Type: ef-disclosure

## Details
# Nethermind SMOD consensus flaw


Short description
*
1 sentence description of the bug
SMOD consensus flaw in Nethermind
Attack scenario
*
More detailed description of the attack/bug scenario and unexpected/buggy behaviour
The attacker can cause consensus failures between Nethermind and other execution layer clients, thus splitting the Ethereum network.

Nethermind failed to handle the minimum value of int256 (type(int256).min == 2 ^ 255 == 0x8000000000000000000000000000000000000000000000000000000000000000), producing wrong result of SMOD.

The SMOD operation takes two int256 arguments A and B and calculates A % B. If A is a negative value, the result should be negative too. So the implementation in Nethermind takes the absolute value of A and B, calculates the modulo, negates the result when A is negative.

```csharp
a.Abs(out Int256.Int256 absA);
b.Abs(out Int256.Int256 absB);
absA.Mod(in absB, out Int256.Int256 mod);

int sign = a.Sign;
if (sign < 0)
{
    mod.Neg(out Int256.Int256 res);
    stack.PushSignedInt256(in res);
}
else
{
    stack.PushSignedInt256(in mod);
}
```

However, because Abs(int256.min) == int256.min, absA can be a negative value. In `Int256.Mod`, the same algorithm is applied again to deal with negative input. The final result will be negated twice and stay positive. For example, in Nethermind 0x8000000000000000000000000000000000000000000000000000000000000000 % -3 == 2, but in other clients (geth and besu), the result is -2.
Impact
*
 Describe the effect this may have in a production setting
The attacker can cause consensus failure between Nethermind and other execution layer clients, thus splitting the Ethereum network.

The exploit is very simple and it could be easily reproduced from a patch, so it's a very dangerous bug.
Components
*
Point to the files, functions, and/or specific line numbers where the bug occurs
https://github.com/NethermindEth/nethermind/blob/bdaa1835fc2aeb8eec3394ad0884cd93e4ed3736/src/Nethermind/Nethermind.Evm/VirtualMachine.cs#L885
Reproduction
*
If used any sort of tools/simulations to find the bug, describe in detail how to reproduce the buggy behaviour.
// SPDX-License-Identifier: UNLICENSED

pragma solidity ^0.8.7;

contract SMOD {
    event Result(int256);

    constructor() {
        int256 a = type(int256).min;
        int256 b = -3;
        int256 c = a % b;
        emit Result(c);
        // require(c == -2, "consensus error");
    }
}
Fix
Description of suggested fix, if available
handle the special case of 2^255 (P255), just like SDIV
Details
Any details not covered above
Int256.Mod implementation: https://github.com/NethermindEth/int256/blob/6429c12c25c68378b39ee0d88d9c44e3e347489c/src/Nethermind.Int256/Int256.cs#L323
