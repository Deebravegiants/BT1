# [M] EL-2022-17: Very slow block execution

## Summary
Severity: Medium
Chain: Ethereum (execution layer)
Component: Besu
Published: 2023-05-03
Source: https://gist.github.com/holiman/213cc1a59971279bc984e2957c089af2#file-writeup-md
Type: ef-disclosure

## Details
{
  "00002762-naivefuzz-0": {
    "env": {
      "currentCoinbase": "b94f5374fce5edbc8e2a8697c15331677e6ebf0b",
      "currentDifficulty": "0x20000",
      "currentGasLimit": "0x26e1f476fe1e22",
      "currentNumber": "0x1",
      "currentTimestamp": "0x3e8",
      "previousHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
      "currentBaseFee": "0x10"
    },
    "pre": {
      "0x00000000000000000000000000000000000000f1": {
        "code": "0x600060006000600060226000fa00",
        "balance": "0x0",
        "nonce": "0x0",
        "storage":{}
      },
      "0x0000000000000000000000000000000000000022": {
        "code": "0x60206000f3",
        "balance": "0x0",
        "nonce": "0x0",
        "storage":{}
      },
      "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b": {
        "code": "0x",
        "storage": {},
        "balance": "0xffffffffff",
        "nonce": "0x0"
      }
    },
    "transaction": {
      "gasPrice": "0x10",
      "nonce": "0x0",
      "to": "0x00000000000000000000000000000000000000f1",
      "data": [
        "0xa0c2d24f6c9506189b84f251eddb322811afaac344741d57602a279ab9f871b2cb372ff544d61082e3dd4baa27b76570c013a91e463bfc0337a082dede51"
      ],

_Trimmed to 38 lines — full report: https://gist.github.com/holiman/213cc1a59971279bc984e2957c089af2#file-writeup-md_
