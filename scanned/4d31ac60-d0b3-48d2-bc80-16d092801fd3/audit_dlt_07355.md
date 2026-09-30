# [?] [FAB-13580] Fix peer join high-cap-channel panic

## Summary
Severity: Unknown
Chain: Hyperledger Fabric
Component: hyperledger/fabric
Published: 2019-01-29
Source: https://github.com/hyperledger/fabric/commit/c76c5091213b22bcb351eef22a54c614abd1b112
Type: security-commit

## Details
[FAB-13580] Fix peer join high-cap-channel panic

Currently, when a old version peer wanna join a newer version channel, the
peer will panic and exit. This behavior is unfriendly as will affect all
existing channels for that peer and the client won't get clear
information about the root cause.

This patchset add a ValidateCapabilities before joining the channel, and
return an error message to the client to indicate the problem is due to
the capabilities requirement. And the peer will still run to process all
existing channels.

Corresponding test cases are implemented to verify with valid and
mismatched capabilities.

Change-Id: I2e0b99ce015331725c5d9e58aa633044507790e2
Signed-off-by: Baohua Yang <baohua.yang@oracle.com>
Signed-off-by: Baohua Yang <yangbaohua@gmail.com>

## Patch
### common/channelconfig/util.go
```diff
@@ -15,6 +15,8 @@ import (
 	mspprotos "github.com/hyperledger/fabric/protos/msp"
 	ab "github.com/hyperledger/fabric/protos/orderer"
 	pb "github.com/hyperledger/fabric/protos/peer"
+	"github.com/hyperledger/fabric/protos/utils"
+	"github.com/pkg/errors"
 )
 
 const (
@@ -222,3 +224,52 @@ func ACLValues(acls map[string]string) *StandardConfigValue {
 		value: a,
 	}
 }
+
+// ValidateCapabilities validates whether the peer can meet the capabilities requirement in the given config block
+func ValidateCapabilities(block *cb.Block) error {
+	envelopeConfig, err := utils.ExtractEnvelope(block, 0)
+	if err != nil {
+		return errors.Errorf("failed to %s", err)
+	}
+
+	configEnv := &cb.ConfigEnvelope{}
+	_, err = utils.UnmarshalEnvelopeOfType(envelopeConfig, cb.HeaderType_CONFIG, configEnv)
+	if err != nil {
+		return errors.Errorf("malformed configuration envelope: %s", err)
+	}
+
+	if configEnv.Config == nil {
+		return errors.New("nil config envelope Config")
+	}
+
+	if configEnv.Config.ChannelGroup == nil {
+		return errors.New("no channel configuration was found in the config block")
+	}
+
+	if configEnv.Config.ChannelGroup.Groups == nil {
+		return errors.New("no channel configuration groups are available")
+	}
+
+	_, exists := configEnv.Config.ChannelGroup.Groups[ApplicationGroupKey]
+	if !exists {
+		return errors.Errorf("invalid configuration block, missing %s "+
+			"configuration group", ApplicationGroupKey)
+	}
+
+	cc, err := NewChannelConfig(configEnv.Config.ChannelGroup)
+	if err != nil {
+		return errors.Errorf("no valid channel configuration found due to %s", err)
+	}
+
+	// Check the channel top-level capabilities
+	if err := cc.Capabilities().Supported(); err != nil {
+		return err
+	}
+
+	// Check the application capabilities
+	if err := cc.ApplicationConfig().Capabilities().Supported(); err != nil {
+		return err
+	}
+
+	return nil
+}
```

### common/channelconfig/util_test.go
```diff
@@ -9,9 +9,12 @@ package channelconfig
 import (
 	"testing"
 
+	"github.com/hyperledger/fabric/common/capabilities"
 	cb "github.com/hyperledger/fabric/protos/common"
 	mspprotos "github.com/hyperledger/fabric/protos/msp"
+	ab "github.com/hyperledger/fabric/protos/orderer"
 	pb "github.com/hyperledger/fabric/protos/peer"
+	"github.com/hyperledger/fabric/protos/utils"
 	"github.com/stretchr/testify/assert"
 )
 
@@ -43,3 +46,243 @@ func TestUtilsBasic(t *testing.T) {
 	basicTest(t, ChannelCreationPolicyValue(&cb.Policy{}))
 	basicTest(t, ACLValues(map[string]string{"foo": "fooval", "bar": "barval"}))
 }
+
+// createCfgBlockWithSupportedCapabilities will create a config block that contains valid capabilities and should be accepted by the peer
+func createCfgBlockWithSupportedCapabilities(t *testing.T) *cb.Block {
+	// Create a config
+	config := &cb.Config{
+		Sequence:     0,
+		ChannelGroup: cb.NewConfigGroup(),
+	}
+
+	// construct the config for top group
+	config.ChannelGroup.Version = 0
+	config.ChannelGroup.ModPolicy = AdminsPolicyKey
+	config.ChannelGroup.Values[BlockDataHashingStructureKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.BlockDataHashingStructure{
+			Width: defaultBlockDataHashingStructureWidth,
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	topCapabilities := make(map[string]bool)
+	topCapabilities[capabilities.ChannelV1_1] = true
+	config.ChannelGroup.Values[CapabilitiesKey] = &cb.ConfigValue{
+		Value:     utils.MarshalOrPanic(CapabilitiesValue(topCapabilities).Value()),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Values[ConsortiumKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.Consortium{
+			Name: "testConsortium",
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Values[HashingAlgorithmKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.HashingAlgorithm{
+			Name: defaultHashingAlgorithm,
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Values[OrdererAddressesKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.OrdererAddresses{
+			Addresses: []string{"orderer.example.com"},
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+
+	// construct the config for Application group
+	config.ChannelGroup.Groups[ApplicationGroupKey] = cb.NewConfigGroup()
+	config.ChannelGroup.Groups[ApplicationGroupKey].Version = 0
+	config.ChannelGroup.Groups[ApplicationGroupKey].ModPolicy = AdminsPolicyKey
+	config.ChannelGroup.Groups[ApplicationGroupKey].Policies[ReadersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[ApplicationGroupKey].Policies[WritersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[ApplicationGroupKey].Policies[AdminsPolicyKey] = &cb.ConfigPolicy{}
+	appCapabilities := make(map[string]bool)
+	appCapabilities[capabilities.ApplicationV1_1] = true
+	config.ChannelGroup.Groups[ApplicationGroupKey].Values[CapabilitiesKey] = &cb.ConfigValue{
+		Value:     utils.MarshalOrPanic(CapabilitiesValue(appCapabilities).Value()),
+		ModPolicy: AdminsPolicyKey,
+	}
+
+	// construct the config for Orderer group
+	config.ChannelGroup.Groups[OrdererGroupKey] = cb.NewConfigGroup()
+	config.ChannelGroup.Groups[OrdererGroupKey].Version = 0
+	config.ChannelGroup.Groups[OrdererGroupKey].ModPolicy = AdminsPolicyKey
+	config.ChannelGroup.Groups[OrdererGroupKey].Policies[ReadersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[OrdererGroupKey].Policies[WritersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[OrdererGroupKey].Policies[AdminsPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[BatchSizeKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(
+			&ab.BatchSize{
+				MaxMessageCount:   65535,
+				AbsoluteMaxBytes:  1024000000,
+				PreferredMaxBytes: 1024000000,
+			}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[BatchTimeoutKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(
+			&ab.BatchTimeout{
+				Timeout: "2s",
+			}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	ordererCapabilities := make(map[string]bool)
+	ordererCapabilities[capabilities.OrdererV1_1] = true
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[CapabilitiesKey] = &cb.ConfigValue{
+		Value:     utils.MarshalOrPanic(CapabilitiesValue(ordererCapabilities).Value()),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[ConsensusTypeKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(
+			&ab.ConsensusType{
+				Type: "solo",
+			}),
+		ModPolicy: AdminsPolicyKey,
+	}
+
+	env := &cb.Envelope{
+		Payload: utils.MarshalOrPanic(&cb.Payload{
+			Header: &cb.Header{
+				ChannelHeader: utils.MarshalOrPanic(&cb.ChannelHeader{
+					ChannelId: "testChain",
+					Type:      int32(cb.HeaderType_CONFIG),
+				}),
+			},
+			Data: utils.MarshalOrPanic(&cb.ConfigEnvelope{
+				Config: config,
+			}),
+		}),
+	}
+	configBlock := &cb.Block{
+		Data: &cb.BlockData{
+			Data: [][]byte{[]byte(utils.MarshalOrPanic(env))},
+		},
+	}
+	return configBlock
+}
+
+// createCfgBlockWithUnSupportedCapabilities will create a config block that contains mismatched capabilities and should be rejected by the peer
+func createCfgBlockWithUnsupportedCapabilities(t *testing.T) *cb.Block {
+	// Create a config
+	config := &cb.Config{
+		Sequence:     0,
+		ChannelGroup: cb.NewConfigGroup(),
+	}
+
+	// construct the config for top group
+	config.ChannelGroup.Version = 0
+	config.ChannelGroup.ModPolicy = AdminsPolicyKey
+	config.ChannelGroup.Values[BlockDataHashingStructureKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.BlockDataHashingStructure{
+			Width: defaultBlockDataHashingStructureWidth,
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	topCapabilities := make(map[string]bool)
+	topCapabilities["INCOMPATIBLE_CAPABILITIES"] = true
+	config.ChannelGroup.Values[CapabilitiesKey] = &cb.ConfigValue{
+		Value:     utils.MarshalOrPanic(CapabilitiesValue(topCapabilities).Value()),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Values[ConsortiumKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.Consortium{
+			Name: "testConsortium",
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Values[HashingAlgorithmKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.HashingAlgorithm{
+			Name: defaultHashingAlgorithm,
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Values[OrdererAddressesKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(&cb.OrdererAddresses{
+			Addresses: []string{"orderer.example.com"},
+		}),
+		ModPolicy: AdminsPolicyKey,
+	}
+
+	// construct the config for Application group
+	config.ChannelGroup.Groups[ApplicationGroupKey] = cb.NewConfigGroup()
+	config.ChannelGroup.Groups[ApplicationGroupKey].Version = 0
+	config.ChannelGroup.Groups[ApplicationGroupKey].ModPolicy = AdminsPolicyKey
+	config.ChannelGroup.Groups[ApplicationGroupKey].Policies[ReadersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[ApplicationGroupKey].Policies[WritersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[ApplicationGroupKey].Policies[AdminsPolicyKey] = &cb.ConfigPolicy{}
+	appCapabilities := make(map[string]bool)
+	appCapabilities["INCOMPATIBLE_CAPABILITIES"] = true
+	config.ChannelGroup.Groups[ApplicationGroupKey].Values[CapabilitiesKey] = &cb.ConfigValue{
+		Value:     utils.MarshalOrPanic(CapabilitiesValue(appCapabilities).Value()),
+		ModPolicy: AdminsPolicyKey,
+	}
+
+	// construct the config for Orderer group
+	config.ChannelGroup.Groups[OrdererGroupKey] = cb.NewConfigGroup()
+	config.ChannelGroup.Groups[OrdererGroupKey].Version = 0
+	config.ChannelGroup.Groups[OrdererGroupKey].ModPolicy = AdminsPolicyKey
+	config.ChannelGroup.Groups[OrdererGroupKey].Policies[ReadersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[OrdererGroupKey].Policies[WritersPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[OrdererGroupKey].Policies[AdminsPolicyKey] = &cb.ConfigPolicy{}
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[BatchSizeKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(
+			&ab.BatchSize{
+				MaxMessageCount:   65535,
+				AbsoluteMaxBytes:  1024000000,
+				PreferredMaxBytes: 1024000000,
+			}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[BatchTimeoutKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(
+			&ab.BatchTimeout{
+				Timeout: "2s",
+			}),
+		ModPolicy: AdminsPolicyKey,
+	}
+	ordererCapabilities := make(map[string]bool)
+	ordererCapabilities["INCOMPATIBLE_CAPABILITIES"] = true
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[CapabilitiesKey] = &cb.ConfigValue{
+		Value:     utils.MarshalOrPanic(CapabilitiesValue(ordererCapabilities).Value()),
+		ModPolicy: AdminsPolicyKey,
+	}
+	config.ChannelGroup.Groups[OrdererGroupKey].Values[ConsensusTypeKey] = &cb.ConfigValue{
+		Value: utils.MarshalOrPanic(
+			&ab.ConsensusType{
+				Type: "solo",
+			}),
+		ModPolicy: AdminsPolicyKey,
+	}
+
+	env := &cb.Envelope{
+		Payload: utils.MarshalOrPanic(&cb.Payload{
+			Header: &cb.Header{
+				ChannelHeader: utils.MarshalOrPanic(&cb.ChannelHeader{
+					ChannelId: "testChain",
+					Type:      int32(cb.HeaderType_CONFIG),
+				}),
+			},
+			Data: utils.MarshalOrPanic(&cb.ConfigEnvelope{
+				Config: config,
+			}),
+		}),
+	}
+	configBlock := &cb.Block{
+		Data: &cb.BlockData{
+			Data: [][]byte{[]byte(utils.MarshalOrPanic(env))},
+		},
+	}
+	return configBlock
+}
+
+func TestValidateCapabilities(t *testing.T) {
+
+	// Test config block with valid capabilities requirement
+	cfgBlock := createCfgBlockWithSupportedCapabilities(t)
+	assert.Nil(t, ValidateCapabilities(cfgBlock), "Should return Nil with matched capabilities checking")
+
+	// Test config block with invalid capabilities requirement
+	cfgBlock = createCfgBlockWithUnsupportedCapabilities(t)
+	assert.NotNil(t, ValidateCapabilities(cfgBlock), "Should return Error with mismatched capabilities checking")
+
+}
```

### core/scc/cscc/configure.go
```diff
@@ -149,6 +149,7 @@ func (e *PeerConfiger) InvokeNoShim(args [][]byte, sp *pb.SignedProposal) pb.Res
 				"channel id from the block due to [%s]", err))
 		}
 
+		// 1. check config block's format and capabilities requirement.
 		if err := validateConfigBlock(block); err != nil {
 			return shim.Error(fmt.Sprintf("\"JoinChain\" for chainID = %s failed because of validation "+
 				"of configuration block, because of %s", cid, err))
@@ -232,6 +233,11 @@ func validateConfigBlock(block *common.Block) error {
 			"configuration group", channelconfig.ApplicationGroupKey)
 	}
 
+	// Check the capabilities requirement
+	if err = channelconfig.ValidateCapabilities(block); err != nil {
+		return errors.Errorf("Failed capabilities check: [%s]", err)
+	}
+
 	return nil
 }
 
```
