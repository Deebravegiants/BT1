# [M] EL-2026-11: Transactions other than Legacy allows for V-values of 27 and 28

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Nethermind
Source: https://notes.ethereum.org/aKEJo8qLTwCDi6DlmD5yKg
Type: ef-disclosure

## Details
ISSUE 3 - Transactions other than Legacy allows for V-values of 27 and 28.
GIT COMMIT: 052355f5e2b1726552fdb38a94cf6ea1506caf95
DESCRIPTION: The sender address derivation and transaction validation allows for transactions of type other than Legacy to have a V-value of 27 and 28.
RLP POC: DynamicFee transaction type with V of 27
02f87501830923b8847744d64085032bc8bf31825208947697666e85053cf587fd07aec8fec308164910bc873c6568f12e800080c01ba05cada95e7ac9b4591249e2f02ef01df5a8c390be6aaea0fb1a1eeadde52a50a6a05dfaa2c2a360d2070edb033ff0b0a3fdaa27a2134784adfa4c3efdc557aeab5c
GO-ETHEREUM ERROR: invalid sender
NETHERMIND ERROR: None
RELEVANT CODE:
Nethermind.Consensus/Validators/TxValidator.cs:

ValidateSignature considers a V value of 27 or 28 always valid

    private bool ValidateSignature(Transaction tx, IReleaseSpec spec)
    {
        Signature? signature = tx.Signature;

        if (signature is null)
        {
            return false;
        }

        UInt256 sValue = new(signature.SAsSpan, isBigEndian: true);
        UInt256 rValue = new(signature.RAsSpan, isBigEndian: true);

        if (sValue.IsZero || sValue >= (spec.IsEip2Enabled ? Secp256K1Curve.HalfNPlusOne : Secp256K1Curve.N))
        {
            return false;
        }

        if (rValue.IsZero || rValue >= Secp256K1Curve.NMinusOne)
        {
            return false;
        }
        
        if (signature.V is 27 or 28)
        {
            return true;
        }

_Trimmed to 38 lines — full report: https://notes.ethereum.org/aKEJo8qLTwCDi6DlmD5yKg_
