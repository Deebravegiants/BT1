# [M] Array is `push()`ed but not `pop()`ed, and is iterated over

## Summary
Severity: Medium
Chain: Smart contract
Component: 2022-01-dev-test-repo
Published: 2023-12-20
Source: https://github.com/code-423n4/2022-01-dev-test-repo-findings/issues/378
Type: code-finding

## Details
### Lines of code

--------------

[96](https://github.com/Tapioca-DAO/tapiocaz-audit/blob/bcf61f79464cfdc0484aa272f9f6e28d5de36a8f/contracts/TapiocaWrapper.sol#L96-L100), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [485](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L485-L494), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [505](https://github.com/Tapioca-DAO/tap-token-audit/blob/59749be5bc2286f0bdbf59d7ddc258ddafd49a9f/contracts/governance/twTAP.sol#L505-L517), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [664](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/bigBang/BigBang.sol#L664-L678), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [105](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L105-L151), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396), [382](https://github.com/Tapioca-DAO/tapioca-bar-audit/blob/2286f80f928f41c8bc189d0657d74ba83286c668/contracts/markets/singularity/SGLLiquidation.sol#L382-L396)

### Vulnerability details

-------------

Array entries are added but are never removed. The array is also iterated over while making state changes, which means that it's possible for an attacker to add so many entries to the array that when it's iterated over by another user, the transaction runs out of gas before all of the iterations are complete, leading to a DOS/bricking of the contract.

```solidity
File: contracts/TapiocaWrapper.sol

/// @audit harvestFees() : harvestableTapiocaOFTs[] :  
96       /// @notice Harvest fees from all the deployed TOFT contracts. Fees are transferred to the owner.
97       function harvestFees() external {
98           for (uint256 i = 0; i < harvestableTapiocaOFTs.length; i++) {
99               harvestableTapiocaOFTs[i].harvestFees();
100:         }

```



```solidity
File: contracts/governance/twTAP.sol

/// @audit claimRewards() : rewardTokens[] :  
/// @audit setTwTap() : rewardTokens[] :  
/// @audit 0() : rewardTokens[] :  
/// @audit claimAndSendRewards() : rewardTokens[] :  
/// @audit exitPositionAndSendTap() : rewardTokens[] :  
/// @audit participate() : rewardTokens[] :  
/// @audit newEpoch() : rewardTokens[] :  
/// @audit exitPosition() : rewardTokens[] :  
/// @audit releaseTap() : rewardTokens[] :  
/// @audit exerciseOption() : rewardTokens[] :  
485          uint256 len = amounts.length;
486          unchecked {
487              for (uint256 i = 0; i < len; ++i) {
488                  uint256 amount = amounts[i];
489                  if (amount > 0) {
490                      // Math is safe: `amount` calculated safely in `claimable()`
491                      claimed[_tokenId][i] += amount;
492                      rewardTokens[i].safeTransfer(_to, amount);
493                  }
494:             }

/// @audit claimAndSendRewards() : rewardTokens[] :  
/// @audit setTwTap() : rewardTokens[] :  
/// @audit 0() : rewardTokens[] :  
/// @audit exitPositionAndSendTap() : rewardTokens[] :  
/// @audit participate() : rewardTokens[] :  
/// @audit newEpoch() : rewardTokens[] :  
/// @audit exitPosition() : rewardTokens[] :  
/// @audit releaseTap() : rewardTokens[] :  
/// @audit exerciseOption() : rewardTokens[] :  
505          unchecked {
506              uint256 len = _rewardTokens.length;
507              for (uint256 i = 0; i < len; ) {
508                  uint256 claimableIndex = rewardTokenIndex[_rewardTokens[i]];
509                  uint256 amount = amounts[i];
510  
511                  if (amount > 0) {
512                      // Math is safe: `amount` calculated safely in `claimable()`
513                      claimed[_tokenId][claimableIndex] += amount;
514                      rewardTokens[claimableIndex].safeTransfer(_to, amount);
515                  }
516                  ++i;
517:             }

```



```solidity
File: contracts/markets/bigBang/BigBang.sol

/// @audit liquidate() : assets[] :  toAmount(), _isSolvent()
/// @audit accrue() : assets[] :  toAmount(), _isSolvent()
/// @audit liquidate() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit accrue() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit liquidate() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit accrue() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit liquidate() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit accrue() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit liquidate() : assets[] :  toShare(), _liquidateUser()
/// @audit accrue() : assets[] :  toShare(), _liquidateUser()
/// @audit liquidate() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit accrue() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
664      ) private {
665          uint256 liquidatedCount = 0;
666          for (uint256 i = 0; i < users.length; i++) {
667              address user = users[i];
668              if (!_isSolvent(user, _exchangeRate)) {
669                  liquidatedCount++;
670                  _liquidateUser(
671                      user,
672                      maxBorrowParts[i],
673                      swapper,
674                      _exchangeRate,
675                      swapData
676                  );
677              }
678:         }

```



```solidity
File: contracts/markets/singularity/SGLLiquidation.sol

/// @audit init() : assets[] :  toAmount(), _isSolvent()
/// @audit liquidate() : assets[] :  toAmount(), _isSolvent()
/// @audit sellCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit repay() : assets[] :  toAmount(), _isSolvent()
/// @audit buyCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit borrow() : assets[] :  toAmount(), _isSolvent()
/// @audit removeCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit addCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit multiHopBuyCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit multiHopSellCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit init() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit liquidate() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit sellCollateral() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit repay() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit buyCollateral() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit borrow() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit removeCollateral() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit addCollateral() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit multiHopBuyCollateral() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit multiHopSellCollateral() : assets[] :  toAmount(), _computeAssetAmountToSolvency()
/// @audit init() : assets[] :  toShare()
/// @audit liquidate() : assets[] :  toShare()
/// @audit sellCollateral() : assets[] :  toShare()
/// @audit repay() : assets[] :  toShare()
/// @audit buyCollateral() : assets[] :  toShare()
/// @audit borrow() : assets[] :  toShare()
/// @audit removeCollateral() : assets[] :  toShare()
/// @audit addCollateral() : assets[] :  toShare()
/// @audit multiHopBuyCollateral() : assets[] :  toShare()
/// @audit multiHopSellCollateral() : assets[] :  toShare()
105          Rebase memory _totalBorrow = totalBorrow;
106  
107          for (uint256 i = 0; i < users.length; i++) {
108              address user = users[i];
109              if (!_isSolvent(user, _exchangeRate)) {
110                  uint256 borrowAmount = _computeAssetAmountToSolvency(
111                      user,
112                      _exchangeRate
113                  );
114  
115                  if (borrowAmount == 0) {
116                      continue;
117                  }
118  
119                  uint256 borrowPart;
120                  {
121                      uint256 availableBorrowPart = userBorrowPart[user];
122                      borrowPart = _totalBorrow.toBase(borrowAmount, false);
123                      userBorrowPart[user] = availableBorrowPart - borrowPart;
124                  }
125                  uint256 amountWithBonus = borrowAmount +
126                      (borrowAmount * liquidationMultiplier) /
127                      FEE_PRECISION;
128                  uint256 collateralShare = yieldBox.toShare(
129                      collateralId,
130                      (amountWithBonus * _exchangeRate) / EXCHANGE_RATE_PRECISION,
131                      false
132                  );
133                  userCollateralShare[user] -= collateralShare;
134                  emit LogRemoveCollateral(
135                      user,
136                      address(liquidationQueue),
137                      collateralShare
138                  );
139                  emit LogRepay(
140                      address(liquidationQueue),
141                      user,
142                      borrowAmount,
143                      borrowPart
144                  );
145  
146                  // Keep totals
147                  allCollateralShare += collateralShare;
148                  allBorrowAmount += borrowAmount;
149                  allBorrowPart += borrowPart;
150              }
151:         }

/// @audit liquidate() : assets[] :  toAmount(), _isSolvent()
/// @audit init() : assets[] :  toAmount(), _isSolvent()
/// @audit sellCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit repay() : assets[] :  toAmount(), _isSolvent()
/// @audit buyCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit borrow() : assets[] :  toAmount(), _isSolvent()
/// @audit removeCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit addCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit multiHopBuyCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit multiHopSellCollateral() : assets[] :  toAmount(), _isSolvent()
/// @audit liquidate() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit init() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit sellCollateral() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit repay() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit buyCollateral() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit borrow() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit removeCollateral() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit addCollateral() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit multiHopBuyCollateral() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit multiHopSellCollateral() : assets[] :  toAmount(), _computeMaxAndMinLTVInAsset(), _liquidateUser()
/// @audit liquidate() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit init() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit sellCollateral() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit repay() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit buyCollateral() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit borrow() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit removeCollateral() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit addCollateral() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit multiHopBuyCollateral() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit multiHopSellCollateral() : assets[] :  toAmount(), _isSolvent(), _liquidateUser()
/// @audit liquidate() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit init() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit sellCollateral() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit repay() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit buyCollateral() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit borrow() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit removeCollateral() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit addCollateral() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit multiHopBuyCollateral() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit multiHopSellCollateral() : assets[] :  toAmount(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit liquidate() : assets[] :  toShare(), _liquidateUser()
/// @audit init() : assets[] :  toShare(), _liquidateUser()
/// @audit sellCollateral() : assets[] :  toShare(), _liquidateUser()
/// @audit repay() : assets[] :  toShare(), _liquidateUser()
/// @audit buyCollateral() : assets[] :  toShare(), _liquidateUser()
/// @audit borrow() : assets[] :  toShare(), _liquidateUser()
/// @audit removeCollateral() : assets[] :  toShare(), _liquidateUser()
/// @audit addCollateral() : assets[] :  toShare(), _liquidateUser()
/// @audit multiHopBuyCollateral() : assets[] :  toShare(), _liquidateUser()
/// @audit multiHopSellCollateral() : assets[] :  toShare(), _liquidateUser()
/// @audit liquidate() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit init() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit sellCollateral() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit repay() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit buyCollateral() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit borrow() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit removeCollateral() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit addCollateral() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit multiHopBuyCollateral() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
/// @audit multiHopSellCollateral() : assets[] :  toShare(), _updateBorrowAndCollateralShare(), _liquidateUser()
382      ) private {
383          uint256 liquidatedCount = 0;
384          for (uint256 i = 0; i < users.length; i++) {
385              address user = users[i];
386              if (!_isSolvent(user, _exchangeRate)) {
387                  liquidatedCount++;
388                  _liquidateUser(
389                      user,
390                      maxBorrowParts[i],
391                      swapper,
392                      _exchangeRate,
393                      swapData
394                  );
395              }
396:         }

```


### Assessed type

------------

other
