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

_Trimmed to 38 lines — full report: https://notes.ethereum.org/lzl_2mBPTimS9PjkWZMW9w_
