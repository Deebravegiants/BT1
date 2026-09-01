# [?] Bybit - Phishing attack

## Summary
Severity: Unknown
Chain: Ethereum
Component: Bybit
Published: 2025-02-21
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/Bybit_exp.sol
Type: defi-exploit-poc

## Details
Lost: 1.5B

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import {IERC20} from "../interface.sol";

// @KeyInfo - Total Lost : 1.5B (401346 ETH + 8000 mETH + 15000 cmETH + 90375 stETH)
// Attacker : https://etherscan.io/address/0x0fa09c3a328792253f8dee7116848723b72a6d2e
// Attack Contract (Trojan): https://etherscan.io/address/0x96221423681a6d52e184d440a8efcebb105c7242
// Attack Contract (Backdoor): https://etherscan.io/address/0xbdd077f651ebe7f7b3ce16fe5f2b025be2969516
// Vulnerable Contract (Bybit Cold Wallet): https://etherscan.io/address/0x1db92e2eebc8e0c075a02bea49a2935bcd2dfcf4
// Attack Tx (Change masterCopy): https://etherscan.io/tx/0x46deef0f52e3a983b67abf4714448a41dd7ffd6d32d32da69d62081c68ad7882
// Attack Tx (ETH): https://etherscan.io/tx/0xb61413c495fdad6114a7aa863a00b2e3c28945979a10885b12b30316ea9f072c
// Attack Tx (mETH): https://etherscan.io/tx/0xbcf316f5835362b7f1586215173cc8b294f5499c60c029a3de6318bf25ca7b20
// Attack Tx (cmETH): https://etherscan.io/tx/0x847b8403e8a4816a4de1e63db321705cdb6f998fb01ab58f653b863fda988647
// Attack Tx (stETH): https://etherscan.io/tx/0xa284a1bc4c7e0379c924c73fcea1067068635507254b03ebbbd3f4e222c1fae0

// @Info
// Vulnerable Contract Code (Proxy): https://etherscan.io/address/0x1db92e2eebc8e0c075a02bea49a2935bcd2dfcf4#code
// Vulnerable Contract Code (Implementation): https://etherscan.io/address/0x34cfac646f301356faa8b21e94227e3583fe3f5f#code

// @Analysis
// Post-mortem : https://x.com/zachxbt/status/1893211577836302365
// Twitter Guy : https://x.com/SlowMist_Team/status/1892963250385592345
// Hacking God : https://x.com/PatrickAlphaC/status/1893215304135618759

contract Enum {
    enum Operation {
        Call,
        DelegateCall
    }
}

interface IMultisigWallet {
    function getTransactionHash(
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-02/Bybit_exp.sol_
