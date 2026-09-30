# [?] Fix pprof service race condition

## Summary
Severity: Unknown
Chain: Harmony
Component: harmony-one/harmony
Published: 2021-07-19
Source: https://github.com/harmony-one/harmony/commit/cb273387a71c62660d7391cdda070dfae90ef7f3
Type: security-commit

## Details
Fix pprof service race condition

## Patch
### api/service/pprof/service.go
```diff
@@ -50,6 +50,7 @@ var (
 	initOnce sync.Once
 	svc      = &Service{}
 	cpuFile  *os.File
+	lock     sync.Mutex
 )
 
 // NewService creates the new pprof service
@@ -75,11 +76,6 @@ func newService(cfg Config) *Service {
 	}
 	svc.profiles = profiles
 
-	go func() {
-		utils.Logger().Info().Str("address", cfg.ListenAddr).Msg("starting pprof HTTP service")
-		http.ListenAndServe(cfg.ListenAddr, nil)
-	}()
-
 	return svc
 }
 
@@ -94,6 +90,11 @@ func (s *Service) Start() error {
 		return err
 	}
 
+	go func() {
+		utils.Logger().Info().Str("address", s.config.ListenAddr).Msg("starting pprof HTTP service")
+		http.ListenAndServe(s.config.ListenAddr, nil)
+	}()
+
 	if _, ok := s.profiles[CPU]; ok {
 		// The nature of the pprof CPU profile is fundamentally different to the other profiles, because it streams output to a file during profiling.
 		// Thus it has to be started outside of the defined interval.
@@ -177,6 +178,8 @@ func saveProfile(profile Profile, dir string) error {
 
 // restartCpuProfile stops the current CPU profile, if any and then starts a new CPU profile. While profiling in the background, the profile will be buffered and written to a file.
 func restartCpuProfile(dir string) error {
+	lock.Lock()
+	defer lock.Unlock()
 	stopCpuProfile()
 	f, err := newTempFile(dir, CPU, ".pb.gz")
 	if err != nil {
```

### api/service/pprof/service_test.go
```diff
@@ -3,10 +3,14 @@ package pprof
 import (
 	"errors"
 	"fmt"
+	"math/rand"
+	"os"
+	"path/filepath"
 	"reflect"
 	"runtime/pprof"
 	"strings"
 	"testing"
+	"time"
 )
 
 func TestUnpackProfilesIntoMap(t *testing.T) {
@@ -72,6 +76,29 @@ func TestUnpackProfilesIntoMap(t *testing.T) {
 	}
 }
 
+func TestStart(t *testing.T) {
+	input := &Config{
+		Enabled:          true,
+		Folder:           tempTestDir(),
+		ProfileNames:     []string{"cpu"},
+		ProfileIntervals: []int{1},
+	}
+	defer os.RemoveAll(input.Folder)
+	s := NewService(*input)
+	err := s.Start()
+	if assErr := assertError(err, nil); assErr != nil {
+		t.Fatal(assErr)
+	}
+	time.Sleep(1 * time.Second)
+}
+
+func tempTestDir() string {
+	tempDir := os.TempDir()
+	testDir := filepath.Join(tempDir, fmt.Sprintf("pprof-service-test-%d-%d", os.Getpid(), rand.Int()))
+	os.RemoveAll(testDir)
+	return testDir
+}
+
 func assertError(gotErr, expErr error) error {
 	if (gotErr == nil) != (expErr == nil) {
 		return fmt.Errorf("error unexpected [%v] / [%v]", gotErr, expErr)
```
