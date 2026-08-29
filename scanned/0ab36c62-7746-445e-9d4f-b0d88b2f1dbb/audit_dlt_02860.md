# [?] Bebop - Arbitrary user input

## Summary
Severity: Unknown
Chain: Arbitrum
Component: Bebop_dex
Published: 2025-08-12
Source: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/Bebop_dex_exp.sol
Type: defi-exploit-poc

## Details
Lost: 21k USD

```solidity
// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.15;

import "../basetest.sol";
import "../interface.sol";

// @KeyInfo - Total Lost : 21k USD
// Attacker : 0x59537353248d0b12c7fcca56a4e420ffec4abc91
// Attack Contract : 0x091101b0f31833c03dddd5b6411e62a212d05875
// Vulnerable Contract : 0xbeb0b0623f66bE8cE162EbDfA2ec543A522F4ea6
// Attack Tx : https://arbiscan.io/tx/0xe5f8fe69b38613a855dbcb499a2c4ecffe318c620a4c4117bd0e298213b7619d

// @Info
// Vulnerable Contract Code : https://arbiscan.io/address/0xbeb0b0623f66bE8cE162EbDfA2ec543A522F4ea6#code

// @Analysis
// Post-mortem : https://x.com/SuplabsYi/status/1955230173365961128
// Twitter Guy : https://x.com/SuplabsYi/status/1955230173365961128
// Hacking God : https://x.com/SuplabsYi/status/1955230173365961128
pragma solidity ^0.8.0;

struct JamOrder {
    address taker;
    address receiver;
    uint256 expiry;
    uint256 exclusivityDeadline;
    uint256 nonce;
    address executor;
    uint256 partnerInfo;
    address[] sellTokens;
    address[] buyTokens;
    uint256[] sellAmounts;
    uint256[] buyAmounts;
    bool usingPermit2;
}
```

_Trimmed to 38 lines — full report: https://github.com/SunWeb3Sec/DeFiHackLabs/blob/main/src/test/2025-08/Bebop_dex_exp.sol_
