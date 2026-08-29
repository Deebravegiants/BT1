# [H] A position can be permanently lost

## Summary
Severity: High
Chain: Smart contract
Component: 2022-11-bullvbear
Published: 2022-11-21
Source: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/145
Type: sherlock-finding

## Details
Deivitto

high

# A position can be permanently lost

## Summary
A position can be permanently lost
## Vulnerability Detail

## Impact
`transferPosition` is a public function with no source of access control that interacts with value of the contract, bull or bear positions to be specific. There are not safety checks for `address(0)`, so, if called by error with this value, position would be permanently lost.
## Code Snippet
https://github.com/sherlock-audit/2022-11-bullvbear/blob/main/bvb-protocol/src/BvbProtocol.sol#L521-L538

function transferPosition(bytes32 orderHash, bool isBull, address recipient) public {
        // ContractId
        uint contractId = uint(orderHash);
        
        if (isBull) {
            // Check that the msg.sender is the Bull
            require(msg.sender == bulls[contractId], "SENDER_NOT_BULL");

            bulls[contractId] = recipient;
        } else {
            // Check that the msg.sender is the Bear
            require(msg.sender == bears[contractId], "SENDER_NOT_BEAR");

            bears[contractId] = recipient;
        }

        emit TransferedPosition(orderHash, isBull, recipient);
    }


## Tool used

Manual Review

_Trimmed to 38 lines — full report: https://github.com/sherlock-audit/2022-11-bullvbear-judging/issues/145_
