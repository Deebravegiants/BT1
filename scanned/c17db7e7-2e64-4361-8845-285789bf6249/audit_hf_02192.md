# [M] Missing Validity Check in MtAwc

## Summary
Severity: Medium
Contest weight: 0.5918
Dataset id: 12190
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Following the previous section that examines the keygen protocol, we in this section analyze the keysign protocol. As mentioned earlier, the keysign protocol strictly follows the multi-party ECDSA algorithm [23]. This algorithm has ﬁve key inter-dependent phases: commitment, MtA/MtAwc share conversion, 훿 1 reconstruction, 푟 generation, and 푠 generation. The ﬁrst phase guarantees the non-repudiation of chosen random numbers that are extensively used in following phases. The second phase leverages an additively homomorphic scheme, i.e., Paillier encryption, to convert multiplicative shares of a secret to additive ones. This conversion is necessary to ensure the 푡+ 1 parties (instead of 2푡+ 1) are suﬃcient for the ﬁnal signature generation. We notice that the protocol in this second phase requires the share conversion of two sets of random numbers (chosen from the ﬁrst phase) and every pair of players 푃푖 and 푃푗 engages in two multiplicative-to-additive share conversion sub-protocols: MtA and MtAwc. The third phase reconstructs 훿 1 that is needed for the four phase to compute 푟, the random number component of ECDSA. Finally, the ﬁve phase generates the signature component of ECDSA, i.e., 푠.
If we zoom in the second phase, there are two multiplicative-to-additive share conversions: MtA and MtAwc. The diﬀerence is MtAwc performs an extra check to ensure the participating party 푃푖 use the correct secret share value, hence the name as MtA with check.
```solidity
func (t *Node) GetKeySignPhase2MsgSent(re *Response) ([]SendingCheaterEvidence, error) {
    t.KeySignPhase2MsgSent = make([]types.KeySignPhase2Msg, t.P-1)
    errStr := ""
    var evidenceList []SendingCheaterEvidence = make([]SendingCheaterEvidence, 0)
    for k, v := range t.KeySignPhase1MsgReceived { // KeySignPhase1MsgReceived is not self - included
        if !t.CheckSenderRangeProof(v.GetNativeSenderRangeProofK(), v.MessageK, v.GetNativePaillierPubKey()) {
            errStr = errStr + v.LabelFrom + "K\n"
            temp := SendingCheaterEvidence{v.LabelFrom, v.GetNativeSenderRangeProofK(), v.MessageK, v.GetNativePaillierPubKey()}
            evidenceList = append(evidenceList, temp)
        }
        if !t.CheckSenderRangeProof(v.GetNativeSenderRangeProofR(), v.MessageR, v.GetNativePaillierPubKey()) {
            errStr = errStr + v.LabelFrom + "R\n"
            temp := SendingCheaterEvidence{v.LabelFrom, v.GetNativeSenderRangeProofR(), v.MessageR, v.GetNativePaillierPubKey()}
            evidenceList = append(evidenceList, temp)
        }
        if errStr != "" {
            continue
        }
        t.KeySignPhase2MsgSent[k].LabelFrom = t.label
        t.KeySignPhase2MsgSent[k].LabelTo = v.LabelFrom
        var Rk, Rr big.Int
        nTilde, h1, h2 := t.NTilde[v.LabelFrom], t.h1[v.LabelFrom], t.h2[v.LabelFrom]
        pub := v.GetNativePaillierPubKey()
        oneCipher, oneR := PaillierEnc(big.NewInt(1), pub)
        t.KeySignPhase2MsgSent[k].MessageKResponse, Rk = getAnotherPart(v.MessageK, pub, t.randNumArray[k], t.r, oneCipher, oneR)
        t.KeySignPhase2MsgSent[k].MessageRResponse, Rr = getAnotherPart(v.MessageR, pub, t.randNumArray[k], t.prtKey, oneCipher, oneR)
        reR, rePrtKey := re.respond(t.r, t.prtKey)
        proofK := t.GetReceiverRangeProof(reR, t.randNumArray[k], Rk, v.MessageK, v.GetNativePaillierPubKey(), nTilde, h1, h2)
        proofR := t.GetReceiverRangeProof(rePrtKey, t.randNumArray[k], Rr, v.MessageR, v.GetNativePaillierPubKey(), nTilde, h1, h2)
        t.KeySignPhase2MsgSent[k].SetNativeReceiverRangeProofK(proofK)
        t.KeySignPhase2MsgSent[k].SetNativeReceiverRangeProofR(proofR)
    }
    if errStr != "" {
        return evidenceList, errors.New(errStr)
    }
    return nil, nil
}
```
used in the second phase. The share conversions of MtA and MtAwc are processed in the getAnotherPart() subroutine (invoked twice in lines 871 and 872). We notice the extra check required in MtAwc is not performed. The lack of this extra check signiﬁcantly weakens the security guarantee of the entire protocol as a player 푃푖 may provide an incorrect key share to mislead the generation of signature without being detected.
```solidity
func getAnotherPart(message []byte, pubKey *paillier.PubKey, randomNum, ownNum *big.Int, oneCipher []byte, oneR *big.Int) ([]byte, *big.Int) {
    cA := message
    gama := randomNum
    b := ownNum
    pub := pubKey
    encGama := paillier.Mul(pub, oneCipher, gama.Bytes())
    big.NewInt(0).Exp(oneR, gama, pub.Nsq)
    cB := paillier.Mul(pubKey, cA, b.Bytes())
    cB = paillier.Add(pubKey, cB, encGama)
    return cB, nil
}
```

## Recommendation
Ensure MtAwc is indeed MtAwc, not MtA.
Public
