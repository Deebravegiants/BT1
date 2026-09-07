# [M] Unspecific Compiler Version Pragma

## Summary
Severity: Medium
Chain: Smart contract
Component: Convergence-Finance---IBO
Published: 2023-09-06
Source: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/41
Type: hats-finding

## Details
**Github username:** @goheesheng
**Submission hash (on-chain):** 0x446cb46b124596ec6673fcbed77a2bd521e243ed528d34555d24b30885cfcb7e
**Severity:** medium

**Description:**
**Description**
Avoid floating pragmas for non-library contracts.

While floating pragmas make sense for libraries to allow them to be included with multiple different versions of applications, it may be a security risk for application implementations.

A known vulnerable compiler version may accidentally be selected or security tools might fall-back to an older compiler version ending up checking a different EVM compilation that is ultimately deployed on the blockchain.

It is recommended to pin to a concrete compiler version.

**Attachments**

1. **Proof of Concept (PoC) File**
```
  ../hats-audit/contracts/Bond/BondCalculator.sol::12 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/Oracles/CvgOracle.sol::12 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/PresaleVesting/Ibo.sol::24 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/PresaleVesting/VestingCvg.sol::12 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/Token/Cvg.sol::12 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/IBaseTest.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/IBondCalculator.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICrvFactory.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICrvFactoryPlain.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICrvPool.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICrvPoolPlain.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICvg.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICvgAggregatorV3.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICvgControlTower.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/ICvgOracle.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/IERC20.sol::4 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/IERC20Mintable.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/IOperatorFilterRegistry.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/IOracleStruct.sol::2 => pragma solidity ^0.8.0;
  ../hats-audit/contracts/interfaces/IPresaleCvgSeed.sol::2 => pragma solidity ^0.8.0;
```

_Trimmed to 38 lines — full report: https://github.com/hats-finance/Convergence-Finance---IBO-0x0e410e7af8e70fc5bffcdbfbdf1673ee7b3d0777/issues/41_
