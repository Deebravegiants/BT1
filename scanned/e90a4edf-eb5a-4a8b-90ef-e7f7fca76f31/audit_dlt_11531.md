# [?] fix(multiplexer): stop panic when shutting down (#5138)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-app
Published: 2025-07-07
Source: https://github.com/celestiaorg/celestia-app/commit/2254e44a1178f36b5701b8616d5859f937316d15
Type: security-commit

## Details
fix(multiplexer): stop panic when shutting down (#5138)

Closes https://github.com/celestiaorg/celestia-app/issues/5137

An attempt at simplifying the multiplexer cleanup because I could not
understand the existing cleanup procedure.

## Testing

```
./scripts/block-sync.sh --network mocha
<wait a few blocks>
CTRL + C
celestia-appd start --force-no-bbr
<wait a few blocks>
CTRL + C
```

Repeat a few times and could not reproduce the `panic`

## Follow ups

https://github.com/celestiaorg/celestia-app/issues/5178

## Patch
### multiplexer/abci/multiplexer.go
```diff
@@ -8,12 +8,9 @@ import (
 	"math"
 	"net"
 	"os"
-	"os/signal"
 	"path/filepath"
 	"strings"
 	"sync"
-	"sync/atomic"
-	"syscall"
 
 	"cosmossdk.io/log"
 	"github.com/celestiaorg/celestia-app/v5/multiplexer/appd"
@@ -53,9 +50,6 @@ const (
 type Multiplexer struct {
 	logger log.Logger
 	mu     sync.Mutex
-	// done is a hack to prevent the multiplexer from catching the above mutex twice and avoiding mu.TryLock
-	// as that could result in an accidental crash.
-	done atomic.Bool
 
 	svrCtx *server.Context
 	svrCfg serverconfig.Config
@@ -83,13 +77,12 @@ type Multiplexer struct {
 	versions Versions
 	// conn is a grpc client connection and used when creating remote ABCI connections.
 	conn *grpc.ClientConn
-	// cleanupFns is a list of functions which should execute upon cleanup of the multiplexer.
-	// any returned errors are logged.
-	cleanupFns []func() error
 	// ctx is the context which is passed to the comet, grpc and api server starting functions.
 	ctx context.Context
 	// g is the waitgroup to which the comet, grpc and api server init functions are added to.
 	g *errgroup.Group
+	// traceWriter is the trace writer for the multiplexer.
+	traceWriter io.WriteCloser
 }
 
 // NewMultiplexer creates a new Multiplexer.
@@ -108,7 +101,6 @@ func NewMultiplexer(svrCtx *server.Context, svrCfg serverconfig.Config, clientCt
 		versions:      versions,
 		chainID:       chainID,
 		appVersion:    applicationVersion,
-		cleanupFns:    make([]func() error, 0),
 	}
 
 	return mp, nil
@@ -129,11 +121,6 @@ func (m *Multiplexer) isGrpcOnly() bool {
 	return m.svrCtx.Viper.GetBool(flagGRPCOnly)
 }
 
-// registerCleanupFn enables the registration of additional cleanup functions that get called during Cleanup
-func (m *Multiplexer) registerCleanupFn(cleanUpFn func() error) {
-	m.cleanupFns = append(m.cleanupFns, cleanUpFn)
-}
-
 func (m *Multiplexer) Start() error {
 	m.g, m.ctx = getCtx(m.svrCtx, true)
 
@@ -386,14 +373,11 @@ func (m *Multiplexer) startAPIServer(grpcSrv *grpc.Server, metrics *telemetry.Me
 
 // startNativeApp starts a native app.
 func (m *Multiplexer) startNativeApp() (servertypes.Application, error) {
-	traceWriter, traceCleanupFn, err := setupTraceWriter(m.svrCtx)
+	traceWriter, err := getTraceWriter(m.svrCtx)
 	if err != nil {
 		return nil, err
 	}
-	m.registerCleanupFn(func() error {
-		traceCleanupFn()
-		return nil
-	})
+	m.traceWriter = traceWriter
 
 	home := m.svrCtx.Config.RootDir
 	db, err := openDB(home, server.GetAppDBBackend(m.svrCtx.Viper))
@@ -402,36 +386,18 @@ func (m *Multiplexer) startNativeApp() (servertypes.Application, error) {
 	}
 
 	m.logger.Debug("creating native app", "app_version", m.appVersion)
-	m.nativeApp = m.appCreator(m.logger, db, traceWriter, m.svrCtx.Viper)
+	m.nativeApp = m.appCreator(m.logger, db, m.traceWriter, m.svrCtx.Viper)
 	m.started = true
-
-	m.registerCleanupFn(func() error {
-		return m.nativeApp.Close()
-	})
-
 	return m.nativeApp, nil
 }
 
-func setupTraceWriter(svrCtx *server.Context) (traceWriter io.WriteCloser, cleanup func(), err error) {
-	// clean up the traceWriter when the server is shutting down
-	cleanup = func() {}
-
+func getTraceWriter(svrCtx *server.Context) (traceWriter io.WriteCloser, err error) {
 	traceWriterFile := svrCtx.Viper.GetString(flagTraceStore)
 	traceWriter, err = openTraceWriter(traceWriterFile)
 	if err != nil {
-		return traceWriter, cleanup, err
-	}
-
-	// if flagTraceStore is not used then traceWriter is nil
-	if traceWriter != nil {
-		cleanup = func() {
-			if err = traceWriter.Close(); err != nil {
-				svrCtx.Logger.Error("failed to close trace writer", "err", err)
-			}
-		}
+		return nil, err
 	}
-
-	return traceWriter, cleanup, nil
+	return traceWriter, nil
 }
 
 func openDB(rootDir string, backendType db.BackendType) (db.DB, error) {
@@ -454,10 +420,6 @@ func openTraceWriter(traceWriterFile string) (w io.WriteCloser, err error) {
 
 // getApp gets the appropriate app based on the latest application version.
 func (m *Multiplexer) getApp() (servertypes.ABCI, error) {
-	// hack to get around the multiplexer hitting its own mutex twice or relying on mu.TryLock.
-	if m.done.Load() {
-		return nil, errors.New("multiplexer already stopped")
-	}
 	m.mu.Lock()
 	defer m.mu.Unlock()
 	m.logger.Debug("getting app", "app_version", m.appVersion, "next_app_version", m.nextAppVersion)
@@ -550,51 +512,6 @@ func (m *Multiplexer) embeddedVersionRunning() bool {
 	return m.activeVersion.Appd != nil && m.activeVersion.Appd.Pid() != appd.AppdStopped
 }
 
-// stopEmbeddedApp stops any embedded app versions if they are currently running.
-func (m *Multiplexer) stopEmbeddedApp() error {
-	if m.embeddedVersionRunning() {
-		m.logger.Info("stopping app for version", "active_app_version", m.activeVersion.AppVersion)
-		if err := m.activeVersion.Appd.Stop(); err != nil {
-			return fmt.Errorf("failed to stop app for version %d: %w", m.activeVersion.AppVersion, err)
-		}
-		m.started = false
-		m.activeVersion = Version{}
-	}
-	return nil
-}
-
-// Cleanup allows proper multiplexer termination.
-func (m *Multiplexer) Cleanup() error {
-	m.done.Store(true)
-	m.mu.Lock()
-	defer m.mu.Unlock()
-
-	m.logger.Info("cleaning up multiplexer")
-
-	var errs error
-
-	// stop any running app
-	if err := m.stopEmbeddedApp(); err != nil {
-		errs = errors.Join(errs, fmt.Errorf("failed to stop active version: %w", err))
-	}
-
-	// close gRPC connection
-	if m.conn != nil {
-		if err := m.conn.Close(); err != nil {
-			errs = errors.Join(errs, fmt.Errorf("failed to close gRPC connection: %w", err))
-		}
-		m.conn = nil
-	}
-
-	for _, fn := range m.cleanupFns {
-		if err := fn(); err != nil {
-			errs = errors.Join(errs, fmt.Errorf("failed to run cleanup function: %w", err))
-		}
-	}
-
-	return errs
-}
-
 // startCmtNode initializes and starts a CometBFT node, sets up cleanup tasks, and assigns it to the Multiplexer instance.
 func (m *Multiplexer) startCmtNode() error {
 	cfg := m.svrCtx.Config
@@ -603,13 +520,7 @@ func (m *Multiplexer) startCmtNode() error {
 		return err
 	}
 
-	// no latest app set means an embedded app is being used.
-	if m.nativeApp == nil {
-		m.logger.Debug("using embedded app so registering remote app cleanup")
-		m.setupRemoteAppCleanup(m.Cleanup)
-	}
-
-	tmNode, err := node.NewNodeWithContext(
+	cmNode, err := node.NewNodeWithContext(
 		m.ctx,
 		cfg,
 		pvm.LoadOrGenFilePV(cfg.PrivValidatorKeyFile(), cfg.PrivValidatorStateFile()),
@@ -624,43 +535,93 @@ func (m *Multiplexer) startCmtNode() error {
 		return err
 	}
 
-	if err := tmNode.Start(); err != nil {
+	if err := cmNode.Start(); err != nil {
 		return err
 	}
 
-	m.registerCleanupFn(func() error {
-		if tmNode != nil && tmNode.IsRunning() {
-			return tmNode.Stop()
-		}
-		return nil
-	})
+	m.cmNode = cmNode
+	return nil
+}
 
-	m.cmNode = tmNode
+// Stop stops the multiplexer and all its components. It intentionally proceeds
+// even if an error occurs in order to shut down as many components as possible.
+func (m *Multiplexer) Stop() error {
+	m.logger.Info("stopping multiplexer")
+	if err := m.stopCometNode(); err != nil {
+		fmt.Println(err)
+	}
+	if err := m.stopNativeApp(); err != nil {
+		fmt.Println(err)
+	}
+	if err := m.stopEmbeddedApp(); err != nil {
+		fmt.Println(err)
+	}
+	if err := m.stopGRPCConnection(); err != nil {
+		fmt.Println(err)
+	}
+	if err := m.stopTraceWriter(); err != nil {
+		fmt.Println(err)
+	}
 	return nil
 }
 
-// setupRemoteAppCleanup ensures that remote app processes are terminated when the main process receives termination signals
-func (m *Multiplexer) setupRemoteAppCleanup(cleanupFn func() error) {
-	sigCh := make(chan os.Signal, 1)
-	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)
+func (m *Multiplexer) stopCometNode() error {
+	if m.cmNode == nil {
+		return nil
+	}
+	if !m.cmNode.IsRunning() {
+		return nil
+	}
+	m.logger.Info("stopping comet node")
+	if err := m.cmNode.Stop(); err != nil {
+		return fmt.Errorf("failed to stop comet node: %w", err)
+	}
+	return nil
+}
 
-	go func() {
-		sig := <-sigCh
-		m.logger.Info("Received signal, stopping remote apps...", "signal", sig)
+func (m *Multiplexer) stopNativeApp() error {
+	if m.nativeApp == nil {
+		return nil
+	}
+	m.logger.Info("stopping native app")
+	if err := m.nativeApp.Close(); err != nil {
+		return fmt.Errorf("failed to close native app: %w", err)
+	}
+	return nil
+}
 
-		if err := cleanupFn(); err != nil {
-			m.logger.Error("Error stopping remote apps", "err", err)
-		} else {
-			m.logger.Info("Successfully stopped remote apps")
-		}
+// stopEmbeddedApp stops any embedded app versions if they are currently running.
+func (m *Multiplexer) stopEmbeddedApp() error {
+	if !m.embeddedVersionRunning() {
+		return nil
+	}
+	m.logger.Info("stopping embedded app for version", "active_app_version", m.activeVersion.AppVersion)
+	if err := m.activeVersion.Appd.Stop(); err != nil {
+		return fmt.Errorf("failed to stop embedded app for version %d: %w", m.activeVersion.AppVersion, err)
+	}
+	m.started = false
+	m.activeVersion = Version{}
+	return nil
+}
 
-		// Re-send the signal to allow the normal process termination
-		signal.Reset(os.Interrupt, syscall.SIGTERM)
-		err := syscall.Kill(os.Getpid(), sig.(syscall.Signal))
-		if err != nil {
-			m.logger.Error("Error killing process", "err", err)
-		}
-	}()
+func (m *Multiplexer) stopGRPCConnection() error {
+	if m.conn == nil {
+		return nil
+	}
+	m.logger.Info("stopping gRPC connection for ABCI")
+	if err := m.conn.Close(); err != nil {
+		return fmt.Errorf("failed to close gRPC connection: %w", err)
+	}
+	m.conn = nil
+	return nil
+}
+
+func (m *Multiplexer) stopTraceWriter() error {
+	if m.traceWriter == nil {
+		return nil
+	}
+	m.logger.Info("stopping trace writer")
+	return m.traceWriter.Close()
 }
 
 func startTelemetry(cfg serverconfig.Config) (*telemetry.Metrics, error) {
```

### multiplexer/appd/run.go
```diff
@@ -10,6 +10,7 @@ import (
 	"os"
 	"os/exec"
 	"path/filepath"
+	"syscall"
 )
 
 const (
@@ -70,18 +71,28 @@ func (a *Appd) Start(args ...string) error {
 	cmd.Stdout = a.stdout
 	cmd.Stderr = a.stderr
 
+	// Start the embedded binary in its own process group.
+	// This prevents the embedded binary from receiving CTRL+C signals directly from the terminal.
+	// That way, the multiplexer can shut down the embedded binary after shutting down CometBFT.
+	cmd.SysProcAttr = &syscall.SysProcAttr{
+		Setpgid: true,
+		Pgid:    0,
+	}
+
 	if err := cmd.Start(); err != nil {
 		return fmt.Errorf("failed to start %s: %w", a.path, err)
 	}
 
 	a.pid = cmd.Process.Pid
+
 	go func() {
-		// wait for process to finish
+		// This waits whether process exits naturally or is killed by Stop()
 		if err := cmd.Wait(); err != nil {
 			log.Printf("Process finished with error: %v\n", err)
+		} else {
+			log.Printf("Process finished with no error\n")
 		}
-
-		a.pid = -1 // reset pid
+		a.pid = AppdStopped // Always reset PID when process ends
 	}()
 
 	return nil
@@ -98,7 +109,7 @@ func (a *Appd) Stop() error {
 		return fmt.Errorf("failed to find process with PID %d: %w", a.pid, err)
 	}
 
-	// send SIGTERM for graceful shutdown
+	// Send SIGTERM for graceful shutdown
 	if err := process.Signal(os.Interrupt); err != nil {
 		log.Printf("Failed to send interrupt signal, attempting to kill: %v", err)
 		// if interrupt fails, try harder with Kill
@@ -107,13 +118,6 @@ func (a *Appd) Stop() error {
 		}
 	}
 
-	// Wait for the process to exit
-	_, err = process.Wait()
-	if err != nil {
-		log.Printf("Error waiting for process to exit: %v", err)
-	}
-
-	a.pid = AppdStopped
 	return nil
 }
 
```

### multiplexer/cmd/start.go
```diff
@@ -31,19 +31,19 @@ func start(versions abci.Versions, svrCtx *server.Context, clientCtx client.Cont
 
 	svrCtx.Logger.Info("initializing multiplexer", "app_version", appVersion, "chain_id", chainID)
 
-	mp, err := abci.NewMultiplexer(svrCtx, svrCfg, clientCtx, appCreator, versions, chainID, appVersion)
+	multiplexer, err := abci.NewMultiplexer(svrCtx, svrCfg, clientCtx, appCreator, versions, chainID, appVersion)
 	if err != nil {
 		return err
 	}
 
 	defer func() {
-		if err := mp.Cleanup(); err != nil {
-			svrCtx.Logger.Error("failed to cleanup multiplexer", "err", err)
+		if err := multiplexer.Stop(); err != nil {
+			svrCtx.Logger.Error("failed to stop multiplexer", "err", err)
 		}
 	}()
 
 	// Start will either start the latest app natively, or an embedded app if one is specified.
-	if err := mp.Start(); err != nil {
+	if err := multiplexer.Start(); err != nil {
 		return fmt.Errorf("failed to start multiplexer: %w", err)
 	}
 
```
