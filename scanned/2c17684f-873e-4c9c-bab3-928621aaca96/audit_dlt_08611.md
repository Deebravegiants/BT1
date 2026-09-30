# [?] task- fix deadlock and mac gpu ct

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/lotus
Published: 2023-10-31
Source: https://github.com/filecoin-project/lotus/commit/e37c87400401b27bc5e7cabd57294b408e0b6884
Type: security-commit

## Details
task- fix deadlock and mac gpu ct

## Patch
### lib/harmony/harmonytask/harmonytask.go
```diff
@@ -4,7 +4,6 @@ import (
 	"context"
 	"fmt"
 	"strconv"
-	"sync"
 	"sync/atomic"
 	"time"
 
@@ -100,7 +99,6 @@ type TaskEngine struct {
 	ctx            context.Context
 	handlers       []*taskTypeHandler
 	db             *harmonydb.DB
-	workAdderMutex sync.Mutex
 	reg            *resources.Reg
 	grace          context.CancelFunc
 	taskMap        map[string]*taskTypeHandler
@@ -289,33 +287,14 @@ func (e *TaskEngine) pollerTryAllWork() {
 	}
 }
 
+// ResourcesAvailable determines what resources are still unassigned.
 func (e *TaskEngine) ResourcesAvailable() resources.Resources {
-	e.workAdderMutex.Lock()
-	defer e.workAdderMutex.Unlock()
-	return e.resoourcesAvailable()
-}
-
-// resoourcesAvailable requires workAdderMutex to be already locked.
-func (e *TaskEngine) resoourcesAvailable() resources.Resources {
 	tmp := e.reg.Resources
-	copy(tmp.GpuRam, e.reg.Resources.GpuRam)
 	for _, t := range e.handlers {
 		ct := t.Count.Load()
 		tmp.Cpu -= int(ct) * t.Cost.Cpu
 		tmp.Gpu -= float64(ct) * t.Cost.Gpu
 		tmp.Ram -= uint64(ct) * t.Cost.Ram
-		if len(t.Cost.GpuRam) == 0 {
-			continue
-		}
-		for i := int32(0); i < ct; i++ {
-			for grIdx, j := range tmp.GpuRam {
-				if j > t.Cost.GpuRam[0] {
-					tmp.GpuRam[grIdx] = 0 // Only 1 per GPU. j - t.Cost.GpuRam[0]
-					break
-				}
-			}
-			log.Warn("We should never get out of gpuram for what's consumed.")
-		}
 	}
 	return tmp
 }
```

### lib/harmony/harmonytask/task_type_handler.go
```diff
@@ -10,7 +10,6 @@ import (
 	"time"
 
 	logging "github.com/ipfs/go-log/v2"
-	"github.com/samber/lo"
 
 	"github.com/filecoin-project/lotus/lib/harmony/harmonydb"
 )
@@ -50,6 +49,11 @@ func (h *taskTypeHandler) AddTask(extra func(TaskID, *harmonydb.Tx) (bool, error
 	}
 }
 
+// considerWork is called to attempt to start work on a task-id of this task type.
+// It presumes single-threaded calling, so there should not be a multi-threaded re-entry.
+// The only caller should be the one work poller thread. This does spin off other threads,
+// but those should not considerWork. Work completing may lower the resource numbers
+// unexpectedly, but that will not invalidate work being already able to fit.
 func (h *taskTypeHandler) considerWork(from string, ids []TaskID) (workAccepted bool) {
 top:
 	if len(ids) == 0 {
@@ -64,10 +68,8 @@ top:
 		return false
 	}
 
-	h.TaskEngine.workAdderMutex.Lock()
-	defer h.TaskEngine.workAdderMutex.Unlock()
-
-	// 2. Can we do any more work?
+	// 2. Can we do any more work? From here onward, we presume the resource
+	// story will not change, so single-threaded calling is best.
 	err := h.AssertMachineHasCapacity()
 	if err != nil {
 		log.Debugw("did not accept task", "name", h.Name, "reason", "at capacity already: "+err.Error())
@@ -213,7 +215,7 @@ func (h *taskTypeHandler) recordCompletion(tID TaskID, workStart time.Time, done
 }
 
 func (h *taskTypeHandler) AssertMachineHasCapacity() error {
-	r := h.TaskEngine.resoourcesAvailable()
+	r := h.TaskEngine.ResourcesAvailable()
 
 	if r.Cpu-h.Cost.Cpu < 0 {
 		return errors.New("Did not accept " + h.Name + " task: out of cpu")
@@ -224,16 +226,5 @@ func (h *taskTypeHandler) AssertMachineHasCapacity() error {
 	if r.Gpu-h.Cost.Gpu < 0 {
 		return errors.New("Did not accept " + h.Name + " task: out of available GPU")
 	}
-	gpuRamSum := lo.Sum(h.Cost.GpuRam)
-	if gpuRamSum == 0 {
-		goto enoughGpuRam
-	}
-	for _, u := range r.GpuRam {
-		if u >= gpuRamSum {
-			goto enoughGpuRam
-		}
-	}
-	return errors.New("Did not accept " + h.Name + " task: out of GPURam")
-enoughGpuRam:
 	return nil
 }
```

### lib/harmony/resources/getGPU.go
```diff
@@ -0,0 +1,21 @@
+//go:build !darwin
+// +build !darwin
+
+package resources
+
+import (
+	"strings"
+
+	ffi "github.com/filecoin-project/filecoin-ffi"
+)
+
+func getGPUDevices() float64 { // GPU boolean
+	gpus, err := ffi.GetGPUDevices()
+	if err != nil {
+		logger.Errorf("getting gpu devices failed: %+v", err)
+	}
+	all := strings.ToLower(strings.Join(gpus, ","))
+	if len(gpus) > 1 || strings.Contains(all, "ati") || strings.Contains(all, "nvidia") {
+		return float64(len(gpus))
+	}
+}
```

### lib/harmony/resources/getGPU_darwin.go
```diff
@@ -0,0 +1,8 @@
+//go:build darwin
+// +build darwin
+
+package resources
+
+func getGPUDevices() float64 {
+	return 10000.0 // unserious value intended for non-production use.
+}
```

### lib/harmony/resources/resources.go
```diff
@@ -7,27 +7,21 @@ import (
 	"os/exec"
 	"regexp"
 	"runtime"
-	"strings"
 	"sync/atomic"
 	"time"
 
 	logging "github.com/ipfs/go-log/v2"
 	"github.com/pbnjay/memory"
-	"github.com/samber/lo"
 	"golang.org/x/sys/unix"
 
-	ffi "github.com/filecoin-project/filecoin-ffi"
-
 	"github.com/filecoin-project/lotus/lib/harmony/harmonydb"
-	cl "github.com/filecoin-project/lotus/lib/harmony/resources/miniopencl"
 )
 
 var LOOKS_DEAD_TIMEOUT = 10 * time.Minute // Time w/o minute heartbeats
 
 type Resources struct {
 	Cpu       int
 	Gpu       float64
-	GpuRam    []uint64
 	Ram       uint64
 	MachineID int
 }
@@ -54,21 +48,20 @@ func Register(db *harmonydb.DB, hostnameAndPort string) (*Reg, error) {
 		if err != nil {
 			return nil, fmt.Errorf("could not read from harmony_machines: %w", err)
 		}
-		gpuram := uint64(lo.Sum(reg.GpuRam))
 		if len(ownerID) == 0 {
 			err = db.QueryRow(ctx, `INSERT INTO harmony_machines 
 		(host_and_port, cpu, ram, gpu, gpuram) VALUES
-		($1,$2,$3,$4,$5) RETURNING id`,
-				hostnameAndPort, reg.Cpu, reg.Ram, reg.Gpu, gpuram).Scan(&reg.Resources.MachineID)
+		($1,$2,$3,$4,0) RETURNING id`,
+				hostnameAndPort, reg.Cpu, reg.Ram, reg.Gpu).Scan(&reg.Resources.MachineID)
 			if err != nil {
 				return nil, err
 			}
 
 		} else {
 			reg.MachineID = ownerID[0]
 			_, err := db.Exec(ctx, `UPDATE harmony_machines SET
-		   cpu=$1, ram=$2, gpu=$3, gpuram=$4 WHERE id=$5`,
-				reg.Cpu, reg.Ram, reg.Gpu, gpuram, reg.Resources.MachineID)
+		   cpu=$1, ram=$2, gpu=$3 WHERE id=$5`,
+				reg.Cpu, reg.Ram, reg.Gpu, reg.Resources.MachineID)
 			if err != nil {
 				return nil, err
 			}
@@ -121,45 +114,14 @@ func getResources() (res Resources, err error) {
 	}
 
 	res = Resources{
-		Cpu:    runtime.NumCPU(),
-		Ram:    memory.FreeMemory(),
-		GpuRam: getGpuRam(),
-	}
-
-	{ // GPU boolean
-		gpus, err := ffi.GetGPUDevices()
-		if err != nil {
-			logger.Errorf("getting gpu devices failed: %+v", err)
-		}
-		all := strings.ToLower(strings.Join(gpus, ","))
-		if len(gpus) > 1 || strings.Contains(all, "ati") || strings.Contains(all, "nvidia") {
-			res.Gpu = float64(len(gpus))
-		}
+		Cpu: runtime.NumCPU(),
+		Ram: memory.FreeMemory(),
+		Gpu: getGPUDevices(),
 	}
 
 	return res, nil
 }
 
-func getGpuRam() (res []uint64) {
-	platforms, err := cl.GetPlatforms()
-	if err != nil {
-		logger.Error(err)
-		return res
-	}
-
-	lo.ForEach(platforms, func(p *cl.Platform, i int) {
-		d, err := p.GetAllDevices()
-		if err != nil {
-			logger.Error(err)
-			return
-		}
-		lo.ForEach(d, func(d *cl.Device, i int) {
-			res = append(res, uint64(d.GlobalMemSize()))
-		})
-	})
-	return res
-}
-
 func DiskFree(path string) (uint64, error) {
 	s := unix.Statfs_t{}
 	err := unix.Statfs(path, &s)
```
