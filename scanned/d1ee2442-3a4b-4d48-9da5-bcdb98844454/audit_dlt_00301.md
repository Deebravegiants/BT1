# [M] EL-2026-08: Envelope transaction incorrectly allows Legacy (type 0) transactions

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Nethermind
Source: https://notes.ethereum.org/5DZ2Gn5ATqS4mydXspU4LA
Type: ef-disclosure

## Details
ISSUE 0 - Envelope transaction type allows for TxType.Legacy
GIT COMMIT: 052355f5e2b1726552fdb38a94cf6ea1506caf95
DESCRIPTION: Nethermind allows for using 0 as type of the legacy transaction type, go-ethereum does not. It is unclear to me from the specification whether type 0 transactions should be allowed to be enveloped.
RLP POC: Transaction envelope with transaction type 0
00f8a9058503b9aca00082b41d94dac17f958d2ee523a2206206994597c13d831ec780b844a9059cbb00000000000000000000000012eaeb963bf185d22531111953b3f73e0e1665dd00000000000000000000000000000000000000000000000000000045d36ed70025a0f4f7a7fa38f8798a95981959aa34d06a7f4cce2ef95b59db575c253e71f9a9f9a011bf69e2d5741cd02bb4d1ed46429b5a6f050457463430dc9875f3199e01abd7
GO-ETHEREUM ERROR: transaction type not supported
NETHERMIND ERROR: None
RELEVANT CODE:

Nethermind.Serialization.Rlp/TxDecoder.cs: Two overloaded Decode functions which read the transaction type. Both locations need to be fixed. The code looks like this:

    T transaction = NewTx();
    if ((rlpBehaviors & RlpBehaviors.SkipTypedWrapping) == RlpBehaviors.SkipTypedWrapping)
    {
        byte firstByte = rlpStream.PeekByte();
        if (firstByte <= 0x7f) // it is typed transactions
        {
            transactionSequence = rlpStream.Peek(rlpStream.Length);
            transaction.Type = (TxType)rlpStream.ReadByte();
        }
    }
    else
    {
        if (!rlpStream.IsSequenceNext())
        {
            (int _, int contentLength) = rlpStream.ReadPrefixAndContentLength();
            transactionSequence = rlpStream.Peek(contentLength);
            transaction.Type = (TxType)rlpStream.ReadByte();
        }
    }

Since c# allows for enums to go out of range, Type can be any value. Therefore the type is later verified in 
Nethermind.Consensus/Validators/TxValidator.cs:IsWellFormed which calls ValidateTxType which looks like this

    private static bool ValidateTxType(Transaction transaction, IReleaseSpec releaseSpec) =>
        transaction.Type switch
        {
            TxType.Legacy => true,

_Trimmed to 38 lines — full report: https://notes.ethereum.org/5DZ2Gn5ATqS4mydXspU4LA_
