# [?] belts and braces around scaling factors to avoid panic (#1734)

## Summary
Severity: Unknown
Chain: Quicksilver
Component: quicksilver-zone/quicksilver
Published: 2024-10-29
Source: https://github.com/quicksilver-zone/quicksilver/commit/4c015b54959be330149920629adc0707f08830b5
Type: security-commit

## Details
belts and braces around scaling factors to avoid panic (#1734)

* boots and braces around scaling factors to avoid panic; shouldnt be needed most cases, but introduced issue with bump in osmosis libs

* fix lint

* fix imports

* add expected values to the tvs test

* update test name to be more meaningful

* lint

---------

Co-authored-by: Ajaz Ahmed <53616488+ajansari95@users.noreply.github.com>

## Patch
### x/participationrewards/keeper/distribution.go
```diff
@@ -10,6 +10,8 @@ import (
 
 	sdk "github.com/cosmos/cosmos-sdk/types"
 
+	"github.com/quicksilver-zone/quicksilver/third-party-chains/osmosis-types/gamm/pool-models/stableswap"
+	"github.com/quicksilver-zone/quicksilver/third-party-chains/osmosis-types/poolmanager"
 	"github.com/quicksilver-zone/quicksilver/utils"
 	"github.com/quicksilver-zone/quicksilver/utils/addressutils"
 	icstypes "github.com/quicksilver-zone/quicksilver/x/interchainstaking/types"
@@ -69,12 +71,12 @@ func (k *Keeper) CalcTokenValues(ctx sdk.Context) (TokenValues, error) {
 
 		if pool.PoolData == nil {
 			errs[idxLabel] = fmt.Errorf("pool data is nil, awaiting OsmosisPoolUpdateCallback")
-			return true
+			return false
 		}
 		gammPool, err := pool.GetPool()
 		if err != nil {
 			errs[idxLabel] = err
-			return true
+			return false
 		}
 
 		denoms := utils.Keys(pool.Denoms)
@@ -88,10 +90,22 @@ func (k *Keeper) CalcTokenValues(ctx sdk.Context) (TokenValues, error) {
 			}
 		}
 
+		if gammPool.GetType() == poolmanager.Stableswap {
+			// be defensive. if scaling_factors are missing, avoid panic.
+			ss, ok := gammPool.(*stableswap.Pool)
+			if !ok {
+				errs[idxLabel] = fmt.Errorf("gammPool %d cannot be cast to StableswapPool", pool.PoolID)
+				return false
+			}
+			if len(ss.GetScalingFactors()) != 2 {
+				errs[idxLabel] = fmt.Errorf("gammPool %d is missing scaling factors", pool.PoolID)
+				return false
+			}
+		}
 		value, err := gammPool.SpotPrice(ctx, denoms[0], denoms[1])
 		if err != nil {
 			errs[idxLabel] = err
-			return true
+			return false
 		}
 
 		decVal := sdk.NewDecFromBigIntWithPrec(value.Dec().BigInt(), 18)
@@ -107,7 +121,7 @@ func (k *Keeper) CalcTokenValues(ctx sdk.Context) (TokenValues, error) {
 		ipool, err := types.UnmarshalProtocolData(types.ProtocolDataTypeOsmosisCLPool, data.Data)
 		if err != nil {
 			errs[idxLabel] = err
-			return true
+			return false
 		}
 		pool, _ := ipool.(*types.OsmosisClPoolProtocolData)
 
@@ -118,12 +132,12 @@ func (k *Keeper) CalcTokenValues(ctx sdk.Context) (TokenValues, error) {
 
 		if pool.PoolData == nil {
 			errs[idxLabel] = fmt.Errorf("pool data is nil, awaiting OsmosisClPoolUpdateCallback")
-			return true
+			return false
 		}
 		clPool, err := pool.GetPool()
 		if err != nil {
 			errs[idxLabel] = err
-			return true
+			return false
 		}
 
 		denoms := utils.Keys(pool.Denoms)
@@ -139,7 +153,7 @@ func (k *Keeper) CalcTokenValues(ctx sdk.Context) (TokenValues, error) {
 		value, err := clPool.SpotPrice(ctx, denoms[0], denoms[1])
 		if err != nil {
 			errs[idxLabel] = err
-			return true
+			return false
 		}
 
 		decVal := sdk.NewDecFromBigIntWithPrec(value.Dec().BigInt(), 18)
```

### x/participationrewards/keeper/distribution_test.go
```diff
@@ -192,3 +192,83 @@ func (suite *KeeperTestSuite) TestCalcTokenValues() {
 		})
 	}
 }
+
+func (suite *KeeperTestSuite) TestCalcTokenValuesIncCLPools() {
+	qs := suite.GetQuicksilverApp(suite.chainA)
+	ctx := suite.chainA.GetContext()
+	osmoParams := types.OsmosisParamsProtocolData{
+		ChainID:   "osmosis-1",
+		BaseDenom: "uosmo",
+		BaseChain: "osmosis-1",
+	}
+	osmoParamsJSON, err := json.Marshal(osmoParams)
+	suite.NoError(err)
+	data := types.ProtocolData{
+		Type: types.ProtocolDataType_name[int32(types.ProtocolDataTypeOsmosisParams)],
+		Data: osmoParamsJSON,
+	}
+	qs.ParticipationRewardsKeeper.SetProtocolData(ctx, osmoParams.GenerateKey(), &data)
+
+	pools := []types.OsmosisPoolProtocolData{}
+	err = json.Unmarshal([]byte(prodPDString), &pools)
+	suite.NoError(err)
+	for _, pool := range pools {
+		poolJSON, err := json.Marshal(pool)
+		suite.NoError(err)
+		data := types.ProtocolData{
+			Type: types.ProtocolDataType_name[int32(types.ProtocolDataTypeOsmosisPool)],
+			Data: poolJSON,
+		}
+		qs.ParticipationRewardsKeeper.SetProtocolData(ctx, pool.GenerateKey(), &data)
+	}
+
+	clpools := []types.OsmosisClPoolProtocolData{}
+	err = json.Unmarshal([]byte(prodPDString2), &clpools)
+	suite.NoError(err)
+	for _, pool := range clpools {
+		poolJSON, err := json.Marshal(pool)
+		suite.NoError(err)
+		data := types.ProtocolData{
+			Type: types.ProtocolDataType_name[int32(types.ProtocolDataTypeOsmosisCLPool)],
+			Data: poolJSON,
+		}
+		qs.ParticipationRewardsKeeper.SetProtocolData(ctx, pool.GenerateKey(), &data)
+	}
+
+	tvs, err := qs.ParticipationRewardsKeeper.CalcTokenValues(ctx)
+	suite.NoError(err)
+	expected := map[string]sdk.Dec{
+		"uatom":   sdk.MustNewDecFromStr("12.677691539450075775"),
+		"ujuno":   sdk.MustNewDecFromStr("0.252676989792765540"),
+		"uosmo":   sdk.MustNewDecFromStr("1.000000000000000000"),
+		"uqatom":  sdk.MustNewDecFromStr("16.637863612013346262"),
+		"uqosmo":  sdk.MustNewDecFromStr("1.201708298212189075"),
+		"uqregen": sdk.MustNewDecFromStr("0.069536169040918330"),
+		"uqsomm":  sdk.MustNewDecFromStr("0.073765486093994849"),
+		"uqstars": sdk.MustNewDecFromStr("0.029935583655522436"),
+		"uregen":  sdk.MustNewDecFromStr("0.052839431713034795"),
+		"usomm":   sdk.MustNewDecFromStr("0.069792907126472964"),
+		"ustars":  sdk.MustNewDecFromStr("0.021812145938948139"),
+	}
+
+	for denom, expectedValue := range expected {
+		suite.Equal(tvs[denom], expectedValue)
+	}
+}
+
+var prodPDString = `[
+	  {"PoolID":1,"PoolName":"ATOM/OSMO","LastUpdated":"2024-06-29T17:00:50.109029446Z","PoolData":{"address":"osmo1mw0ac6rwlp5r8wapwk3zs6g29h8fcscxqakdzw9emkne6c8wjp9q0t3v8t","id":1,"pool_params":{"swap_fee":"0.002000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"24h","total_shares":{"denom":"gamm/pool/1","amount":"51756990084398530307168264"},"pool_assets":[{"token":{"denom":"ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2","amount":"575276315709"},"weight":"536870912000000"},{"token":{"denom":"uosmo","amount":"7293175680510"},"weight":"536870912000000"}],"total_weight":"1073741824000000"},"PoolType":"balancer","Denoms":{"ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2":{"Denom":"uatom","ChainID":"cosmoshub-4"},"uosmo":{"Denom":"uosmo","ChainID":"osmosis-1"}},"IsIncentivized":false},
+	  {"PoolID":1087,"PoolName":"SOMM/qSOMM","LastUpdated":"2024-06-29T17:09:07.817925952Z","PoolData":{"address":"osmo1unwajz776rcsvaaehrq82qldwfw4zeqp7jgty09cw4lytuwfw3pqvs0cmt","id":1087,"pool_params":{"swap_fee":"0.003000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"168h","total_shares":{"denom":"gamm/pool/1087","amount":"1052495305723789511288418"},"pool_liquidity":[{"denom":"ibc/9BBA9A1C257E971E38C1422780CE6F0B0686F0A3085E2D61118D904BFE0F5F5E","amount":"105275083846"},{"denom":"ibc/EAF76AD1EEF7B16D167D87711FB26ABE881AC7D9F7E6D0CF313D5FA530417208","amount":"107870858010"}],"scaling_factors":[1057053811,1000000000],"scaling_factor_governor":"osmo16x03wcp37kx5e8ehckjxvwcgk9j0cqnhm8m3yy"},"PoolType":"stableswap","Denoms":{"ibc/9BBA9A1C257E971E38C1422780CE6F0B0686F0A3085E2D61118D904BFE0F5F5E":{"Denom":"usomm","ChainID":"sommelier-3"},"ibc/EAF76AD1EEF7B16D167D87711FB26ABE881AC7D9F7E6D0CF313D5FA530417208":{"Denom":"uqsomm","ChainID":"sommelier-3"}},"IsIncentivized":true},
+	  {"PoolID":42,"PoolName":"REGEN/OSMO","LastUpdated":"2024-06-29T17:01:08.083152922Z","PoolData":{"address":"osmo1txawpctjs6phpqsnkx2r5qud7yvekw93394anhuzz4dquy5jggssgqtn0l","id":42,"pool_params":{"swap_fee":"0.002000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"24h","total_shares":{"denom":"gamm/pool/42","amount":"26509813273140138926958"},"pool_assets":[{"token":{"denom":"ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076","amount":"853135473387"},"weight":"536870912000000"},{"token":{"denom":"uosmo","amount":"45079193588"},"weight":"536870912000000"}],"total_weight":"1073741824000000"},"PoolType":"balancer","Denoms":{"ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076":{"Denom":"uregen","ChainID":"regen-1"},"uosmo":{"Denom":"uosmo","ChainID":"osmosis-1"}},"IsIncentivized":false},
+	  {"PoolID":497,"PoolName":"JUNO/OSMO","LastUpdated":"2024-06-29T17:01:37.013088205Z","PoolData":{"address":"osmo1h7yfu7x4qsv2urnkl4kzydgxegdfyjdry5ee4xzj98jwz0uh07rqdkmprr","id":497,"pool_params":{"swap_fee":"0.003000000000000000","exit_fee":"0.000000000000000000"},"total_shares":{"denom":"gamm/pool/497","amount":"148794601473627832073337"},"pool_assets":[{"token":{"denom":"ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED","amount":"573672533941"},"weight":"536870912000000"},{"token":{"denom":"uosmo","amount":"144953849003"},"weight":"536870912000000"}],"total_weight":"1073741824000000"},"PoolType":"balancer","Denoms":{"ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED":{"Denom":"ujuno","ChainID":"juno-1"},"uosmo":{"Denom":"uosmo","ChainID":"osmosis-1"}},"IsIncentivized":false},
+	  {"PoolID":604,"PoolName":"STARS/OSMO","LastUpdated":"2024-06-29T17:02:07.675839861Z","PoolData":{"address":"osmo1thscstwxp87g0ygh7le3h92f9ff4sel9y9d2eysa25p43yf43rysk7jp93","id":604,"pool_params":{"swap_fee":"0.003000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"24h","total_shares":{"denom":"gamm/pool/604","amount":"27287206734846955128"},"pool_assets":[{"token":{"denom":"ibc/987C17B11ABC2B20019178ACE62929FE9840202CE79498E29FE8E5CB02B7C0A4","amount":"6981654162834"},"weight":"21474836480"},{"token":{"denom":"uosmo","amount":"152284859495"},"weight":"21474836480"}],"total_weight":"42949672960"},"PoolType":"balancer","Denoms":{"ibc/987C17B11ABC2B20019178ACE62929FE9840202CE79498E29FE8E5CB02B7C0A4":{"Denom":"ustars","ChainID":"stargaze-1"},"uosmo":{"Denom":"uosmo","ChainID":"osmosis-1"}},"IsIncentivized":false},
+	  {"PoolID":627,"PoolName":"SOMM/OSMO","LastUpdated":"2024-06-29T17:01:37.013088205Z","PoolData":{"address":"osmo19qawwfrlkz9upglmpqj6akgz9ap7v2mnd05pxzgmxw3ywz58wnvqtet2mg","id":627,"pool_params":{"swap_fee":"0.002000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"24h","total_shares":{"denom":"gamm/pool/627","amount":"58898324380432389355671"},"pool_assets":[{"token":{"denom":"ibc/9BBA9A1C257E971E38C1422780CE6F0B0686F0A3085E2D61118D904BFE0F5F5E","amount":"383959778025"},"weight":"536870912000000"},{"token":{"denom":"uosmo","amount":"26797669128"},"weight":"536870912000000"}],"total_weight":"1073741824000000"},"PoolType":"balancer","Denoms":{"ibc/9BBA9A1C257E971E38C1422780CE6F0B0686F0A3085E2D61118D904BFE0F5F5E":{"Denom":"usomm","ChainID":"sommelier-3"},"uosmo":{"Denom":"uosmo","ChainID":"osmosis-1"}},"IsIncentivized":false},
+	  {"PoolID":903,"PoolName":"qSTARS/STARS","LastUpdated":"2024-06-29T17:00:50.109029446Z","PoolData":{"address":"osmo1cxlrfu8r0v3cyqj78fuvlsmhjdgna0r7tum8cpd0g3x7w7pte8fsfvcs84","id":903,"pool_params":{"swap_fee":"0.003000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"24h","total_shares":{"denom":"gamm/pool/903","amount":"33285682356451671868036"},"pool_liquidity":[{"denom":"ibc/46C83BB054E12E189882B5284542DB605D94C99827E367C9192CF0579CD5BC83","amount":"201086272390"},{"denom":"ibc/987C17B11ABC2B20019178ACE62929FE9840202CE79498E29FE8E5CB02B7C0A4","amount":"672153817668"}],"scaling_factors":[1,1]},"PoolType":"stableswap","Denoms":{"ibc/46C83BB054E12E189882B5284542DB605D94C99827E367C9192CF0579CD5BC83":{"Denom":"uqstars","ChainID":"stargaze-1"},"ibc/987C17B11ABC2B20019178ACE62929FE9840202CE79498E29FE8E5CB02B7C0A4":{"Denom":"ustars","ChainID":"stargaze-1"}},"IsIncentivized":true},
+	  {"PoolID":944,"PoolName":"ATOM/qATOM","LastUpdated":"2024-06-29T17:01:08.083152922Z","PoolData":{"address":"osmo1awr39mc2hrkt8gq8gt3882ru40ay45k8a3yg69nyypqe9g0ryycs66lhkh","id":944,"pool_params":{"swap_fee":"0.003000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"168h","total_shares":{"denom":"gamm/pool/944","amount":"376682006004054987881"},"pool_liquidity":[{"denom":"ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2","amount":"3590725451"},{"denom":"ibc/FA602364BEC305A696CBDF987058E99D8B479F0318E47314C49173E8838C5BAC","amount":"3561329984"}],"scaling_factors":[1318616518,1000000000],"scaling_factor_governor":"osmo16x03wcp37kx5e8ehckjxvwcgk9j0cqnhm8m3yy"},"PoolType":"stableswap","Denoms":{"ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2":{"Denom":"uatom","ChainID":"cosmoshub-4"},"ibc/FA602364BEC305A696CBDF987058E99D8B479F0318E47314C49173E8838C5BAC":{"Denom":"uqatom","ChainID":"cosmoshub-4"}},"IsIncentivized":true},
+	  {"PoolID":948,"PoolName":"REGEN/qREGEN","LastUpdated":"2024-06-29T17:00:50.109029446Z","PoolData":{"address":"osmo1hylqy4uu5el36wykhzzhj786eh8rx4epyvg6nrtl503wjufz8z3sdptdzw","id":948,"pool_params":{"swap_fee":"0.003000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"168h","total_shares":{"denom":"gamm/pool/948","amount":"203791959210650860086725"},"pool_liquidity":[{"denom":"ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076","amount":"247440093055"},{"denom":"ibc/79A676508A2ECA1021EDDC7BB9CF70CEEC9514C478DA526A5A8B3E78506C2206","amount":"177233580285"}],"scaling_factors":[1315922033,1000000000],"scaling_factor_governor":"osmo16x03wcp37kx5e8ehckjxvwcgk9j0cqnhm8m3yy"},"PoolType":"stableswap","Denoms":{"ibc/1DCC8A6CB5689018431323953344A9F6CC4D0BFB261E88C9F7777372C10CD076":{"Denom":"uregen","ChainID":"regen-1"},"ibc/79A676508A2ECA1021EDDC7BB9CF70CEEC9514C478DA526A5A8B3E78506C2206":{"Denom":"uqregen","ChainID":"regen-1"}},"IsIncentivized":true},
+	  {"PoolID":956,"PoolName":"qOSMO/OSMO","LastUpdated":"2024-06-29T17:01:08.083152922Z","PoolData":{"address":"osmo1q023e9m4d3ffvr96xwaeraa62yfvufkufkr7yf7lmacgkuspsuqsga4xp2","id":956,"pool_params":{"swap_fee":"0.003000000000000000","exit_fee":"0.000000000000000000"},"future_pool_governor":"168h","total_shares":{"denom":"gamm/pool/956","amount":"2831883387499914752885"},"pool_liquidity":[{"denom":"ibc/42D24879D4569CE6477B7E88206ADBFE47C222C6CAD51A54083E4A72594269FC","amount":"4678864416"},{"denom":"uosmo","amount":"7164359952"}],"scaling_factors":[1000000000,1182092750],"scaling_factor_governor":"osmo16x03wcp37kx5e8ehckjxvwcgk9j0cqnhm8m3yy"},"PoolType":"stableswap","Denoms":{"ibc/42D24879D4569CE6477B7E88206ADBFE47C222C6CAD51A54083E4A72594269FC":{"Denom":"uqosmo","ChainID":"osmosis-1"},"uosmo":{"Denom":"uosmo","ChainID":"osmosis-1"}},"IsIncentivized":true}
+	]`
+
+var prodPDString2 = `[
+	{"PoolID":1590,"PoolName":"qOSMO/OSMO","LastUpdated":"2024-06-29T17:01:08.083152922Z","PoolData":{"address":"osmo1ww5567k7ya8g2rzfft30mgdqwy6jyfqfl60805kclwc3x44qzp6qgd3d3r","incentives_address":"osmo1e0wfxnfrzg50wkeyakg2qxjf4fw9lrtx88grlhuw9n2ajm2sth2sdpg9ky","spread_rewards_address":"osmo1e9grc4jp9jzwqqxy6cv6ypkkytyae50wygc9zsj3w5040a3yq4es6z09q7","id":1590,"current_tick_liquidity":"987929067650.598626855339345890","token0":"ibc/42D24879D4569CE6477B7E88206ADBFE47C222C6CAD51A54083E4A72594269FC","token1":"uosmo","current_sqrt_price":"1.102849323600434041469545632253046567","current_tick":216276,"tick_spacing":100,"exponent_at_price_one":-6,"spread_factor":"0.000500000000000000","last_liquidity_update":"2024-09-16T11:42:46.811999582Z"}, "Denoms":{"ibc/42D24879D4569CE6477B7E88206ADBFE47C222C6CAD51A54083E4A72594269FC":{"Denom":"uqosmo","ChainID":"osmosis-1"},"uosmo":{"Denom":"uosmo","ChainID":"osmosis-1"}},"IsIncentivized":true}
+]`
```
