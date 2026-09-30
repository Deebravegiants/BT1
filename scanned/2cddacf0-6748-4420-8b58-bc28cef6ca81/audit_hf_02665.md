# [M] Lack Of Size Validation Of Byte Arrays Used With BLS

## Summary
Severity: Medium
Contest weight: 0.1269
Dataset id: 14442
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
There are no checks implemented in DeserializeG1() and DeserializeG2() functions of datalayr-mantle/common/crypto/bls/b to verify if provided byte array is of sufficient size:
```go
func DeserializeG1(b []byte) *bn254.G1Affine {
    p := new(bn254.G1Affine)
    p.X.SetBytes(b[0:32])
    p.Y.SetBytes(b[32:64])
    return p
}

func DeserializeG2(b []byte) *bn254.G2Affine {
    p := new(bn254.G2Affine)
    p.X.A0.SetBytes(b[0:32])
    p.X.A1.SetBytes(b[32:64])
    p.Y.A0.SetBytes(b[64:96])
    p.Y.A1.SetBytes(b[96:128])
    return p
}
```
If b parameter array’s size is smaller than 64 for DeserializeG1() or 128 for DeserializeG2(), the function will panic with index out-of-bounds error.
This could be manipulated by dispersers by using StoreFramesRequest via StoreFrames() in datalayr-mantle/dl-node/server.go line [174].

## Recommendation
Implement an additional check to verify that size of the array passed in as b parameter is larger than an expected minimum.
