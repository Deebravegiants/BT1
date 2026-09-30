# [?] resolve usage panic

## Summary
Severity: Unknown
Chain: Kaia
Component: kaiachain/kaia
Published: 2023-07-26
Source: https://github.com/kaiachain/kaia/commit/2fd9f36490bd267bdea93dc895c6a50c5ae47239
Type: security-commit

## Details
resolve usage panic

## Patch
### cmd/homi/setup/flags.go
```diff
@@ -36,8 +36,8 @@ var (
 	genTypeFlag = cli.StringFlag{
 		Name:    "gen-type",
 		Usage:   "Generate environment files according to the type (docker, local, remote, deploy)",
-		Aliases: []string{},
 		Value:   "docker",
+		Aliases: []string{},
 	}
 
 	cypressTestFlag = cli.BoolFlag{
@@ -79,50 +79,50 @@ var (
 	numOfCNsFlag = cli.IntFlag{
 		Name:    "cn-num",
 		Usage:   "Number of consensus nodes",
-		Aliases: []string{"topology.cn-num"},
 		Value:   0,
+		Aliases: []string{"topology.cn-num"},
 	}
 	numOfValidatorsFlag = cli.IntFlag{
 		Name:    "validators-num",
 		Usage:   "Number of validators. If not set, it will be set the number of option cn-num",
-		Aliases: []string{"topology.validators-num"},
 		Value:   0,
+		Aliases: []string{"topology.validators-num"},
 	}
 	numOfPNsFlag = cli.IntFlag{
 		Name:    "pn-num",
 		Usage:   "Number of proxy node",
-		Aliases: []string{"topology.pn-num"},
 		Value:   0,
+		Aliases: []string{"topology.pn-num"},
 	}
 	numOfENsFlag = cli.IntFlag{
 		Name:    "en-num",
 		Usage:   "Number of end-point node",
-		Aliases: []string{"topology.en-num"},
 		Value:   0,
+		Aliases: []string{"topology.en-num"},
 	}
 	numOfSCNsFlag = cli.IntFlag{
 		Name:    "scn-num",
 		Usage:   "Number of service chain nodes",
-		Aliases: []string{"topology.scn-num"},
 		Value:   0,
+		Aliases: []string{"topology.scn-num"},
 	}
 	numOfSPNsFlag = cli.IntFlag{
 		Name:    "spn-num",
 		Usage:   "Number of service chain proxy nodes",
-		Aliases: []string{"topology.spn-num"},
 		Value:   0,
+		Aliases: []string{"topology.spn-num"},
 	}
 	numOfSENsFlag = cli.IntFlag{
 		Name:    "sen-num",
 		Usage:   "Number of service chain end-point nodes",
-		Aliases: []string{"topology.sen-num"},
 		Value:   0,
+		Aliases: []string{"topology.sen-num"},
 	}
 	numOfTestKeyFlag = cli.IntFlag{
 		Name:    "test-num",
 		Usage:   "Number of test key",
-		Aliases: []string{"topology.test-num"},
 		Value:   0,
+		Aliases: []string{"topology.test-num"},
 	}
 
 	genesisTypeFlag = cli.StringFlag{
@@ -145,29 +145,29 @@ var (
 	chainIDFlag = cli.Uint64Flag{
 		Name:    "chainID",
 		Usage:   "ChainID",
-		Aliases: []string{"genesis.chain-id"},
 		Value:   1000,
+		Aliases: []string{"genesis.chain-id"},
 	}
 
 	serviceChainIDFlag = cli.Uint64Flag{
 		Name:    "serviceChainID",
 		Usage:   "Service Chain ID",
-		Aliases: []string{"genesis.service-chain-id"},
 		Value:   1001,
+		Aliases: []string{"genesis.service-chain-id"},
 	}
 
 	unitPriceFlag = cli.Uint64Flag{
 		Name:    "unitPrice",
 		Usage:   "Price of unit",
-		Aliases: []string{"genesis.unit-price"},
 		Value:   0,
+		Aliases: []string{"genesis.unit-price"},
 	}
 
 	deriveShaImplFlag = cli.IntFlag{
 		Name:    "deriveShaImpl",
 		Usage:   "Implementation of DeriveSha [0:Original, 1:Simple, 2:Concat]",
-		Aliases: []string{"genesis.derive-sha-impl"},
 		Value:   0,
+		Aliases: []string{"genesis.derive-sha-impl"},
 	}
 
 	outputPathFlag = cli.StringFlag{
@@ -194,15 +194,15 @@ var (
 	patchAddressBookAddrFlag = cli.StringFlag{
 		Name:    "patch-address-book-addr",
 		Usage:   "The address to inject in AddressBook's constructContract function [default: first CN's address]",
-		Aliases: []string{"genesis.patched-address-book.addr"},
 		Value:   "",
+		Aliases: []string{"genesis.patched-address-book.addr"},
 	}
 	// Deprecated: it doesn't used anymore
 	subGroupSizeFlag = cli.IntFlag{
 		Name:    "subgroup-size",
 		Usage:   "CN's Subgroup size",
-		Aliases: []string{},
 		Value:   21,
+		Aliases: []string{},
 	}
 
 	addressBookMockFlag = cli.BoolFlag{
@@ -225,8 +225,8 @@ var (
 	networkIdFlag = cli.IntFlag{
 		Name:    "network-id",
 		Usage:   "(docker only) network identifier (default : 2018)",
-		Aliases: []string{"deploy.docker.network-id"},
 		Value:   2018,
+		Aliases: []string{"deploy.docker.network-id"},
 	}
 	nografanaFlag = cli.BoolFlag{
 		Name:    "no-grafana",
@@ -241,61 +241,61 @@ var (
 	txGenRateFlag = cli.IntFlag{
 		Name:    "txgen-rate",
 		Usage:   "(docker only) txgen's rate option [default : 2000]",
-		Aliases: []string{"deploy.docker.tx-gen.rate"},
 		Value:   2000,
+		Aliases: []string{"deploy.docker.tx-gen.rate"},
 	}
 	txGenConnFlag = cli.IntFlag{
 		Name:    "txgen-conn",
 		Usage:   "(docker only) txgen's connection size option [default : 100]",
-		Aliases: []string{"deploy.docker.tx-gen.connetions"},
 		Value:   100,
+		Aliases: []string{"deploy.docker.tx-gen.connetions"},
 	}
 	txGenDurFlag = cli.StringFlag{
 		Name:    "txgen-dur",
 		Usage:   "(docker only) txgen's duration option [default : 1m]",
-		Aliases: []string{"deploy.docker.tx-gen.duration"},
 		Value:   "1m",
+		Aliases: []string{"deploy.docker.tx-gen.duration"},
 	}
 	txGenThFlag = cli.IntFlag{
 		Name:    "txgen-th",
 		Usage:   "(docker-only) txgen's thread size option [default : 2]",
-		Aliases: []string{"deploy.docker.tx-gen.thread"},
 		Value:   2,
+		Aliases: []string{"deploy.docker.tx-gen.thread"},
 	}
 
 	rpcPortFlag = cli.IntFlag{
 		Name:    "rpc-port",
 		Usage:   "klay.conf - Klaytn node's rpc port [default: 8551] ",
-		Aliases: []string{"deploy.rpc-port"},
 		Value:   8551,
+		Aliases: []string{"deploy.rpc-port"},
 	}
 
 	wsPortFlag = cli.IntFlag{
 		Name:    "ws-port",
 		Usage:   "klay.conf - Klaytn node's ws port [default: 8552]",
-		Aliases: []string{"deploy.ws-port"},
 		Value:   8552,
+		Aliases: []string{"deploy.ws-port"},
 	}
 
 	p2pPortFlag = cli.IntFlag{
 		Name:    "p2p-port",
 		Usage:   "klay.conf - Klaytn node's p2p port [default: 32323]",
-		Aliases: []string{"deploy.p2p-port"},
 		Value:   32323,
+		Aliases: []string{"deploy.p2p-port"},
 	}
 
 	dataDirFlag = cli.StringFlag{
 		Name:    "data-dir",
 		Usage:   "klay.conf - Klaytn node's data directory path [default : /var/klay/data]",
-		Aliases: []string{"deploy.data-dir"},
 		Value:   "/var/klay/data",
+		Aliases: []string{"deploy.data-dir"},
 	}
 
 	logDirFlag = cli.StringFlag{
 		Name:    "log-dir",
 		Usage:   "klay.conf - Klaytn node's log directory path [default : /var/klay/log]",
-		Aliases: []string{"deploy.log-dir"},
 		Value:   "/var/klay/log",
+		Aliases: []string{"deploy.log-dir"},
 	}
 
 	// Governance flags
@@ -308,15 +308,15 @@ var (
 	govModeFlag = cli.StringFlag{
 		Name:    "gov-mode",
 		Usage:   "governance mode (none, single, ballot) [default: none]",
-		Aliases: []string{"genesis.governance-mode"},
 		Value:   params.DefaultGovernanceMode,
+		Aliases: []string{"genesis.governance-mode"},
 	}
 
 	governingNodeFlag = cli.StringFlag{
 		Name:    "governing-node",
 		Usage:   "the governing node [default: 0x0000000000000000000000000000000000000000]",
-		Aliases: []string{"genesis.governing-node"},
 		Value:   params.DefaultGoverningNode,
+		Aliases: []string{"genesis.governing-node"},
 	}
 
 	govParamContractFlag = cli.StringFlag{
@@ -328,14 +328,14 @@ var (
 	rewardMintAmountFlag = cli.StringFlag{
 		Name:    "reward-mint-amount",
 		Usage:   "governance minting amount",
-		Aliases: []string{"genesis.reward.mint-amount"},
 		Value:   "9600000000000000000",
+		Aliases: []string{"genesis.reward.mint-amount"},
 	}
 	rewardRatioFlag = cli.StringFlag{
 		Name:    "reward-ratio",
 		Usage:   "governance ratio [default: 100/0/0]",
-		Aliases: []string{"genesis.reward.ratio"},
 		Value:   params.DefaultRatio,
+		Aliases: []string{"genesis.reward.ratio"},
 	}
 
 	rewardKip82RatioFlag = cli.StringFlag{
@@ -357,125 +357,125 @@ var (
 	rewardStakingFlag = cli.Uint64Flag{
 		Name:    "reward-staking-interval",
 		Usage:   "reward staking update interval flag",
-		Aliases: []string{"genesis.reward.staking-interval"},
 		Value:   86400,
+		Aliases: []string{"genesis.reward.staking-interval"},
 	}
 	rewardProposerFlag = cli.Uint64Flag{
 		Name:    "reward-proposer-interval",
 		Usage:   "reward proposer update interval flag",
-		Aliases: []string{"genesis.reward.proposer-inteval"},
 		Value:   3600,
+		Aliases: []string{"genesis.reward.proposer-inteval"},
 	}
 	rewardMinimumStakeFlag = cli.StringFlag{
 		Name:    "reward-minimum-stake",
 		Usage:   "reward minimum stake flag",
-		Aliases: []string{"genesis.reward.minimum-stake"},
 		Value:   "2000000",
+		Aliases: []string{"genesis.reward.minimum-stake"},
 	}
 
 	magmaLowerBoundBaseFeeFlag = cli.Uint64Flag{
 		Name:    "lower-bound-base-fee",
 		Usage:   "lower bound base fee flag",
-		Aliases: []string{"genesis.kip71.lower-bound-base-fee"},
 		Value:   params.DefaultLowerBoundBaseFee,
+		Aliases: []string{"genesis.kip71.lower-bound-base-fee"},
 	}
 
 	magmaUpperBoundBaseFeeFlag = cli.Uint64Flag{
 		Name:    "upper-bound-base-fee",
 		Usage:   "upper bound base fee flag",
-		Aliases: []string{"genesis.kip71.upper-bound-base-fee"},
 		Value:   params.DefaultUpperBoundBaseFee,
+		Aliases: []string{"genesis.kip71.upper-bound-base-fee"},
 	}
 
 	magmaGasTarget = cli.Uint64Flag{
 		Name:    "gas-target",
 		Usage:   "gas target flag",
-		Aliases: []string{"genesis.kip71.gas-target"},
 		Value:   params.DefaultGasTarget,
+		Aliases: []string{"genesis.kip71.gas-target"},
 	}
 
 	magmaMaxBlockGasUsedForBaseFee = cli.Uint64Flag{
 		Name:    "block-gas-limit",
 		Usage:   "block gas limit flag",
-		Aliases: []string{"genesis.kip71.block-gas-limit"},
 		Value:   params.DefaultMaxBlockGasUsedForBaseFee,
+		Aliases: []string{"genesis.kip71.block-gas-limit"},
 	}
 
 	magmaBaseFeeDenominator = cli.Uint64Flag{
 		Name:    "base-fee-denominator",
 		Usage:   "base fee denominator flag",
-		Aliases: []string{"genesis.kip71.base-fee-denominator"},
 		Value:   params.DefaultBaseFeeDenominator,
+		Aliases: []string{"genesis.kip71.base-fee-denominator"},
 	}
 
 	istEpochFlag = cli.Uint64Flag{
 		Name:    "ist-epoch",
 		Usage:   "governance epoch [default: 604800]",
-		Aliases: []string{"genesis.consensus.istanbul.epoch"},
 		Value:   params.DefaultEpoch,
+		Aliases: []string{"genesis.consensus.istanbul.epoch"},
 	}
 
 	istProposerPolicyFlag = cli.Uint64Flag{
 		Name:    "ist-proposer-policy",
 		Usage:   "governance proposer policy (0: RoundRobin, 1: Sticky, 2: WeightedRandom) [default: 0]",
-		Aliases: []string{"genesis.consensus.istanbul.policy"},
 		Value:   params.DefaultProposerPolicy,
+		Aliases: []string{"genesis.consensus.istanbul.policy"},
 	}
 
 	istSubGroupFlag = cli.Uint64Flag{
 		Name:    "ist-subgroup",
 		Usage:   "governance subgroup size [default: 21]",
-		Aliases: []string{"genesis.consensus.istanbul.subgroup"},
 		Value:   params.DefaultSubGroupSize,
+		Aliases: []string{"genesis.consensus.istanbul.subgroup"},
 	}
 
 	cliqueEpochFlag = cli.Uint64Flag{
 		Name:    "clique-epoch",
 		Usage:   "clique epoch",
-		Aliases: []string{"genesis.consensus.clique.epoch"},
 		Value:   params.DefaultEpoch,
+		Aliases: []string{"genesis.consensus.clique.epoch"},
 	}
 
 	cliquePeriodFlag = cli.Uint64Flag{
 		Name:    "clique-period",
 		Usage:   "clique period",
-		Aliases: []string{"genesis.consensus.clique.period"},
 		Value:   params.DefaultPeriod,
+		Aliases: []string{"genesis.consensus.clique.period"},
 	}
 
 	istanbulCompatibleBlockNumberFlag = cli.Int64Flag{
 		Name:    "istanbul-compatible-blocknumber",
 		Usage:   "istanbulCompatible blockNumber",
-		Aliases: []string{"genesis.hardfork.istanbul-compatible-blocknumber"},
 		Value:   0,
+		Aliases: []string{"genesis.hardfork.istanbul-compatible-blocknumber"},
 	}
 
 	londonCompatibleBlockNumberFlag = cli.Int64Flag{
 		Name:    "london-compatible-blocknumber",
 		Usage:   "londonCompatible blockNumber",
-		Aliases: []string{"genesis.hardfork.london-compatible-blocknumber"},
 		Value:   0,
+		Aliases: []string{"genesis.hardfork.london-compatible-blocknumber"},
 	}
 
 	ethTxTypeCompatibleBlockNumberFlag = cli.Int64Flag{
 		Name:    "eth-tx-type-compatible-blocknumber",
 		Usage:   "ethTxTypeCompatible blockNumber",
-		Aliases: []string{"genesis.hardfork.eth-tx-type-compatible-blocknumber"},
 		Value:   0,
+		Aliases: []string{"genesis.hardfork.eth-tx-type-compatible-blocknumber"},
 	}
 
 	magmaCompatibleBlockNumberFlag = cli.Int64Flag{
 		Name:    "magma-compatible-blocknumber",
 		Usage:   "magmaCompatible blockNumber",
-		Aliases: []string{"genesis.hardfork.magma-compatible-blocknumber"},
 		Value:   0,
+		Aliases: []string{"genesis.hardfork.magma-compatible-blocknumber"},
 	}
 
 	koreCompatibleBlockNumberFlag = cli.Int64Flag{
 		Name:    "kore-compatible-blocknumber",
 		Usage:   "koreCompatible blockNumber",
-		Aliases: []string{"genesis.hardfork.kore-compatible-blocknumber"},
 		Value:   0,
+		Aliases: []string{"genesis.hardfork.kore-compatible-blocknumber"},
 	}
 
 	kip103CompatibleBlockNumberFlag = cli.Int64Flag{
```

### cmd/utils/usage.go
```diff
@@ -69,7 +69,7 @@ func NewHelpPrinter(fg []FlagGroup) func(w io.Writer, tmp string, data interface
 		} else if tmpl == CommandHelpTemplate {
 			// Iterate over all command specific flags and categorize them
 			categorized := make(map[string][]cli.Flag)
-			for _, flag := range data.(cli.Command).Flags {
+			for _, flag := range data.(*cli.Command).Flags {
 				if _, ok := categorized[flag.String()]; !ok {
 					categorized[flagCategory(flag, fg)] = append(categorized[flagCategory(flag, fg)], flag)
 				}
```
