# [H] function CardTopupTrusted and function CardTopupMPTProof and function _processTopup in HardenedTopupProxy.sol may revert because these functions access msg.value but missing payable keywords.

## Summary
Severity: High
Chain: Smart contract
Component: 2022-10-mover
Published: 2022-10-28
Source: https://github.com/sherlock-audit/2022-10-mover-judging/issues/77
Type: sherlock-finding

## Details
ctf_sec

high

# function CardTopupTrusted and function CardTopupMPTProof and function _processTopup in HardenedTopupProxy.sol may revert because these functions access msg.value but missing payable keywords.

## Summary

function CardTopupTrusted and function CardTopupMPTProof and function _processTopup in HardenedTopupProxy.sol may revert because these functions access msg.value but missing payable keywords.

## Vulnerability Detail

function CardTopupTrusted and function CardTopupMPTProof  in HardenedTopupProxy.sol calls

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L1047

inside this function, we access the msg.value keywords:

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L335-L344

but without payable keywords, accessing msg.value will result in revert.

## Impact

The topup bridge transfer function will not be functional.

## Code Snippet

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L1031

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L1056

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L1047

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L1081

https://github.com/sherlock-audit/2022-10-mover/blob/main/cardtopup_contract/contracts/HardenedTopupProxy.sol#L335-L344


_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-10-mover-judging/issues/77_
