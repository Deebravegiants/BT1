# [M] M-03 | Deployment Scripts Conﬁguration Issues

## Summary
Severity: Medium
Contest weight: 0.1081
Dataset id: 2088
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
1. Incorrect Send Library Conﬁguration:
• The ChainConﬁgurator contract currently sets ChainConﬁg.sendLibrary for Ethereum to
0xD231084BfB234C107D3eE2b22F97F3346fDAF705
• This is the sendUln301 library meant for LayerZero EndpointV1
2. Maximum Message Size:
• The ConﬁgureBeacons contract run script sets ExecutorConﬁg.maxMessageSize to 1_000_000
• This is signiﬁcantly higher than the default executor conﬁguration of 10_000 bytes
3. Send Library Conﬁguration:
• The ConﬁgureBeacons contract run script only sets LayerZero send libraries when they differ from
defaults

## Recommendation
1. Send Library Update:
• Set ChainConﬁg.sendLibrary to 0x21F33EcF7F65D61f77e554B4B4380829908cD076 (SendUln302)
• This ensures compatibility with LayerZero EndpointV2
2. Message Size Standardization:
• Set ExecutorConﬁg.maxMessageSize to the default value of 10_000 bytes
3. Library Conﬁguration:
• Always explicitly set LayerZero libraries
• Do this even when values match defaults
