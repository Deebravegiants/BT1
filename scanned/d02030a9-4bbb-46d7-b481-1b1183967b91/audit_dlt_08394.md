# [?] fix(server/v2/api/telemetry): avoid panic due to no telemetry address (#23022)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2024-12-20
Source: https://github.com/cosmos/cosmos-sdk/commit/422be7044259544b794934922591410d91afb7f2
Type: security-commit

## Details
fix(server/v2/api/telemetry): avoid panic due to no telemetry address (#23022)

## Patch
### server/v2/api/telemetry/config.go
```diff
@@ -59,3 +59,20 @@ type Config struct {
 	// Datadog. Only utilized if MetricsSink is set to "dogstatsd".
 	DatadogHostname string `mapstructure:"datadog-hostname" toml:"data-dog-hostname" comment:"DatadogHostname defines the hostname to use when emitting metrics to Datadog. Only utilized if MetricsSink is set to \"dogstatsd\"."`
 }
+
+// CfgOption is a function that allows to overwrite the default server configuration.
+type CfgOption func(*Config)
+
+// OverwriteDefaultConfig overwrites the default config with the new config.
+func OverwriteDefaultConfig(newCfg *Config) CfgOption {
+	return func(cfg *Config) {
+		*cfg = *newCfg
+	}
+}
+
+// Disable the telemetry server by default (default enabled).
+func Disable() CfgOption {
+	return func(cfg *Config) {
+		cfg.Enable = false
+	}
+}
```

### server/v2/api/telemetry/server.go
```diff
@@ -21,14 +21,15 @@ var (
 const ServerName = "telemetry"
 
 type Server[T transaction.Tx] struct {
-	logger  log.Logger
-	config  *Config
-	server  *http.Server
-	metrics *Metrics
+	logger     log.Logger
+	config     *Config
+	cfgOptions []CfgOption
+	server     *http.Server
+	metrics    *Metrics
 }
 
 // New creates a new telemetry server.
-func New[T transaction.Tx](cfg server.ConfigMap, logger log.Logger, enableTelemetry func()) (*Server[T], error) {
+func New[T transaction.Tx](cfg server.ConfigMap, logger log.Logger, enableTelemetry func(), cfgOptions ...CfgOption) (*Server[T], error) {
 	srv := &Server[T]{}
 	serverCfg := srv.Config().(*Config)
 	if len(cfg) > 0 {
@@ -37,6 +38,7 @@ func New[T transaction.Tx](cfg server.ConfigMap, logger log.Logger, enableTeleme
 		}
 	}
 	srv.config = serverCfg
+	srv.cfgOptions = cfgOptions
 	srv.logger = logger.With(log.ModuleKey, srv.Name())
 
 	if enableTelemetry == nil {
@@ -66,14 +68,29 @@ func New[T transaction.Tx](cfg server.ConfigMap, logger log.Logger, enableTeleme
 	return srv, nil
 }
 
+// NewWithConfigOptions creates a new telemetry server with the provided config options.
+// It is *not* a fully functional server (since it has been created without dependencies)
+// The returned server should only be used to get and set configuration.
+func NewWithConfigOptions[T transaction.Tx](opts ...CfgOption) *Server[T] {
+	return &Server[T]{
+		cfgOptions: opts,
+	}
+}
+
 // Name returns the server name.
 func (s *Server[T]) Name() string {
 	return ServerName
 }
 
 func (s *Server[T]) Config() any {
 	if s.config == nil || s.config.Address == "" {
-		return DefaultConfig()
+		cfg := DefaultConfig()
+		// overwrite the default config with the provided options
+		for _, opt := range s.cfgOptions {
+			opt(cfg)
+		}
+
+		return cfg
 	}
 
 	return s.config
```

### simapp/v2/simdv2/cmd/testnet.go
```diff
@@ -22,6 +22,7 @@ import (
 	"cosmossdk.io/server/v2/api/grpc"
 	"cosmossdk.io/server/v2/api/grpcgateway"
 	"cosmossdk.io/server/v2/api/rest"
+	"cosmossdk.io/server/v2/api/telemetry"
 	"cosmossdk.io/server/v2/cometbft"
 	"cosmossdk.io/server/v2/store"
 	banktypes "cosmossdk.io/x/bank/types"
@@ -183,10 +184,11 @@ func initTestnetFiles[T transaction.Tx](
 		genFiles    []string
 	)
 	const (
-		rpcPort  = 26657
-		apiPort  = 1317
-		grpcPort = 9090
-		restPort = 8080
+		rpcPort       = 26657
+		apiPort       = 1317
+		grpcPort      = 9090
+		restPort      = 8080
+		telemetryPort = 7180
 	)
 	p2pPortStart := 26656
 
@@ -197,6 +199,7 @@ func initTestnetFiles[T transaction.Tx](
 		grpcConfig := grpc.DefaultConfig()
 		grpcgatewayConfig := grpcgateway.DefaultConfig()
 		restConfig := rest.DefaultConfig()
+		telemetryConfig := telemetry.DefaultConfig()
 
 		if args.singleMachine {
 			portOffset = i
@@ -221,6 +224,11 @@ func initTestnetFiles[T transaction.Tx](
 				Enable:  true,
 				Address: fmt.Sprintf("127.0.0.1:%d", restPort+portOffset),
 			}
+
+			telemetryConfig = &telemetry.Config{
+				Enable:  true,
+				Address: fmt.Sprintf("127.0.0.1:%d", telemetryPort+portOffset),
+			}
 		}
 
 		nodeDirName := fmt.Sprintf("%s%d", args.nodeDirPrefix, i)
@@ -356,7 +364,8 @@ func initTestnetFiles[T transaction.Tx](
 		grpcServer := grpc.NewWithConfigOptions[T](grpc.OverwriteDefaultConfig(grpcConfig))
 		grpcgatewayServer := grpcgateway.NewWithConfigOptions[T](grpcgateway.OverwriteDefaultConfig(grpcgatewayConfig))
 		restServer := rest.NewWithConfigOptions[T](rest.OverwriteDefaultConfig(restConfig))
-		server := serverv2.NewServer[T](serverCfg, cometServer, storeServer, grpcServer, grpcgatewayServer, restServer)
+		telemetryServer := telemetry.NewWithConfigOptions[T](telemetry.OverwriteDefaultConfig(telemetryConfig))
+		server := serverv2.NewServer[T](serverCfg, cometServer, storeServer, grpcServer, grpcgatewayServer, restServer, telemetryServer)
 		err = server.WriteConfig(filepath.Join(nodeDir, "config"))
 		if err != nil {
 			return err
```
