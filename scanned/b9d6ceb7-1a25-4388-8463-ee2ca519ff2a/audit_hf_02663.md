# [M] Incorrect Error Returned With Empty Signature

## Summary
Severity: Medium
Contest weight: 0.2119
Dataset id: 14426
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
```go
generateSignature() may return an empty signature data in a successful response.
In SignMessage() of tss/node/tsslib/keysign/tss_keysign.go, if an error is detected when calling SetupIDMaps() an
empty signature data field is returned. However, it is returned with an incorrect error object ( err instead of err1 or
err2 ), meaning that an empty signature will be erroneously used later on:
err1 := conversion.SetupIDMaps(partyIDMap, tKeySign.tssCommonStruct.PartyIDtoP2PID)
err2 := conversion.SetupIDMaps(partyIDMap, abnormalMgr.PartyIDtoP2PID)
if err1 != nil || err2 != nil {
    tKeySign.logger.Error().Err(err).Msgf("error in creating mapping between partyID and P2P ID")
    return emptySignatureData, err
    // @audit this should be either err1 or err2
Then the check in tss/node/tsslib/keysign.go:generateSignature() line [48] will fail (due to err being nil ), re-
turning an empty signature in the successful response on line [59]:
signatureData, err := keysignInstance.SignMessage(req.Message, localStateItem, signers)
// the statistic of keygen only care about Tss it self, even if the following http response aborts,
// it still counted as a successful keygen as the Tss model runs successfully.
if err != nil {
    t.logger.Error().Err(err).Msg("err in keysign")
    culprits := keysignInstance.GetTssCommonStruct().GetAbnormalMgr().TssCulpritsNodes()
    return keysign2.Response{
        Status:
        common.Fail,
        FailReason: abnormal.SignatureError,
        Culprits:
        culprits,
    }, nil
}
return keysign2.NewResponse(
    &signatureData,
    common.Success,
    nil,
), nil
```

## Recommendation
Correct tss/node/tsslib/keysign/tss_keysign.go line [103] to return the relevant err1 or err2 instead of err.
