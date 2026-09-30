# [?] fix(prover):fix prover panic infinite retry (#824)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2023-08-18
Source: https://github.com/scroll-tech/scroll/commit/becfd41b0e14d31684a9c6ad4d866594e5f84798
Type: security-commit

## Details
fix(prover):fix prover panic infinite retry (#824)

Co-authored-by: georgehao <georgehao@users.noreply.github.com>

## Patch
### common/version/version.go
```diff
@@ -6,7 +6,7 @@ import (
 	"strings"
 )
 
-var tag = "v4.1.71"
+var tag = "v4.1.72"
 
 var commit = func() string {
 	if info, ok := debug.ReadBuildInfo(); ok {
```

### go.work.sum
```diff
@@ -193,6 +193,7 @@ github.com/cpuguy83/go-md2man v1.0.10 h1:BSKMNlYxDvnunlTymqtgONjNnaRV1sTpcovwwjF
 github.com/cpuguy83/go-md2man/v2 v2.0.0-20190314233015-f79a8a8ca69d/go.mod h1:maD7wRr/U5Z6m/iR4s+kqSMx2CaBsrgA7czyZG/E6dU=
 github.com/crate-crypto/go-ipa v0.0.0-20220523130400-f11357ae11c7 h1:6IrxszG5G+O7zhtkWxq6+unVvnrm1fqV2Pe+T95DUzw=
 github.com/crate-crypto/go-ipa v0.0.0-20220523130400-f11357ae11c7/go.mod h1:gFnFS95y8HstDP6P9pPwzrxOOC5TRDkwbM+ao15ChAI=
+github.com/crate-crypto/go-ipa v0.0.0-20230601170251-1830d0757c80 h1:DuBDHVjgGMPki7bAyh91+3cF1Vh34sAEdH8JQgbc2R0=
 github.com/crate-crypto/go-ipa v0.0.0-20230601170251-1830d0757c80/go.mod h1:gzbVz57IDJgQ9rLQwfSk696JGWof8ftznEL9GoAv3NI=
 github.com/creack/pty v1.1.11 h1:07n33Z8lZxZ2qwegKbObQohDhXDQxiMMz1NOUGYlesw=
 github.com/creack/pty v1.1.18 h1:n56/Zwd5o6whRC5PMGretI4IdRLlmBXYNjScPaBgsbY=
@@ -238,6 +239,7 @@ github.com/dop251/goja v0.0.0-20220405120441-9037c2b61cbf h1:Yt+4K30SdjOkRoRRm3v
 github.com/dop251/goja v0.0.0-20220405120441-9037c2b61cbf/go.mod h1:R9ET47fwRVRPZnOGvHxxhuZcbrMCuiqOz3Rlrh4KSnk=
 github.com/dop251/goja v0.0.0-20230122112309-96b1610dd4f7 h1:kgvzE5wLsLa7XKfV85VZl40QXaMCaeFtHpPwJ8fhotY=
 github.com/dop251/goja v0.0.0-20230122112309-96b1610dd4f7/go.mod h1:yRkwfj0CBpOGre+TwBsqPV0IH0Pk73e4PXJOeNDboGs=
+github.com/dop251/goja v0.0.0-20230605162241-28ee0ee714f3 h1:+3HCtB74++ClLy8GgjUQYeC8R4ILzVcIe8+5edAJJnE=
 github.com/dop251/goja v0.0.0-20230605162241-28ee0ee714f3/go.mod h1:QMWlm50DNe14hD7t24KEqZuUdC9sOTy8W6XbCU1mlw4=
 github.com/dop251/goja_nodejs v0.0.0-20210225215109-d91c329300e7 h1:tYwu/z8Y0NkkzGEh3z21mSWggMg4LwLRFucLS7TjARg=
 github.com/dop251/goja_nodejs v0.0.0-20210225215109-d91c329300e7/go.mod h1:hn7BA7c8pLvoGndExHudxTDKZ84Pyvv+90pbBjbTz0Y=
@@ -277,6 +279,7 @@ github.com/garslo/gogen v0.0.0-20170306192744-1d203ffc1f61/go.mod h1:Q0X6pkwTILD
 github.com/gavv/httpexpect v2.0.0+incompatible h1:1X9kcRshkSKEjNJJxX9Y9mQ5BRfbxU5kORdjhlA1yX8=
 github.com/gballet/go-verkle v0.0.0-20220902153445-097bd83b7732 h1:AB7YjNrzlVHsYz06zCULVV2zYCEft82P86dSmtwxKL0=
 github.com/gballet/go-verkle v0.0.0-20220902153445-097bd83b7732/go.mod h1:o/XfIXWi4/GqbQirfRm5uTbXMG5NpqxkxblnbZ+QM9I=
+github.com/gballet/go-verkle v0.0.0-20230607174250-df487255f46b h1:vMT47RYsrftsHSTQhqXwC3BYflo38OLC3Y4LtXtLyU0=
 github.com/gballet/go-verkle v0.0.0-20230607174250-df487255f46b/go.mod h1:CDncRYVRSDqwakm282WEkjfaAj1hxU/v5RXxk5nXOiI=
 github.com/getkin/kin-openapi v0.61.0 h1:6awGqF5nG5zkVpMsAih1QH4VgzS8phTxECUWIFo7zko=
 github.com/ghemawat/stream v0.0.0-20171120220530-696b145b53b9 h1:r5GgOLGbza2wVHRzK7aAj6lWZjfbAwiu/RDCVOKjRyM=
@@ -374,6 +377,7 @@ github.com/google/pprof v0.0.0-20200430221834-fc25d7d30c6d/go.mod h1:ZgVRPoUq/hf
 github.com/google/pprof v0.0.0-20200708004538-1a94d8640e99 h1:Ak8CrdlwwXwAZxzS66vgPt4U8yUZX7JwLvVR58FN5jM=
 github.com/google/pprof v0.0.0-20200708004538-1a94d8640e99/go.mod h1:ZgVRPoUq/hfqzAqh7sHMqb3I9Rq5C59dIz2SbBwJ4eM=
 github.com/google/pprof v0.0.0-20210407192527-94a9f03dee38/go.mod h1:kpwsk12EmLew5upagYY7GY0pfYCcupk39gWOCRROcvE=
+github.com/google/pprof v0.0.0-20230207041349-798e818bf904 h1:4/hN5RUoecvl+RmJRE2YxKWtnnQls6rQjjW5oV7qg2U=
 github.com/google/pprof v0.0.0-20230207041349-798e818bf904/go.mod h1:uglQLonpP8qtYCYyzA+8c/9qtqgA3qsXGYqCPKARAFg=
 github.com/google/renameio v0.1.0 h1:GOZbcHa3HfsPKPlmyPyN2KEohoMXOhdMbHrvbpl2QaA=
 github.com/google/shlex v0.0.0-20191202100458-e7afc7fbc510 h1:El6M4kTTCOh6aBiKaUGG7oYTSPP8MxqL4YI3kZKwcP4=
@@ -472,6 +476,7 @@ github.com/k0kubun/colorstring v0.0.0-20150214042306-9440f1994b88 h1:uC1QfSlInpQ
 github.com/karalabe/usb v0.0.0-20211005121534-4c5740d64559/go.mod h1:Od972xHfMJowv7NGVDiWVxk2zxnWgjLlJzE+F4F7AGU=
 github.com/karalabe/usb v0.0.2 h1:M6QQBNxF+CQ8OFvxrT90BA0qBOXymndZnk5q235mFc4=
 github.com/karalabe/usb v0.0.2/go.mod h1:Od972xHfMJowv7NGVDiWVxk2zxnWgjLlJzE+F4F7AGU=
+github.com/karalabe/usb v0.0.3-0.20230711191512-61db3e06439c h1:AqsttAyEyIEsNz5WLRwuRwjiT5CMDUfLk6cFJDVPebs=
 github.com/karalabe/usb v0.0.3-0.20230711191512-61db3e06439c/go.mod h1:Od972xHfMJowv7NGVDiWVxk2zxnWgjLlJzE+F4F7AGU=
 github.com/kataras/blocks v0.0.7 h1:cF3RDY/vxnSRezc7vLFlQFTYXG/yAr1o7WImJuZbzC4=
 github.com/kataras/blocks v0.0.7/go.mod h1:UJIU97CluDo0f+zEjbnbkeMRlvYORtmc1304EeyXf4I=
@@ -711,6 +716,7 @@ go.opentelemetry.io/otel v1.9.0/go.mod h1:np4EoPGzoPs3O67xUVNoPPcmSvsfOxNlNA4F4A
 go.opentelemetry.io/otel/trace v1.9.0 h1:oZaCNJUjWcg60VXWee8lJKlqhPbXAPB51URuR47pQYc=
 go.opentelemetry.io/otel/trace v1.9.0/go.mod h1:2737Q0MuG8q1uILYm2YYVkAyLtOofiTNGg6VODnOiPo=
 go.uber.org/atomic v1.3.2 h1:2Oa65PReHzfn29GpvgsYwloV9AVFHPDk8tYxt2c2tr4=
+go.uber.org/automaxprocs v1.5.2 h1:2LxUOGiR3O6tw8ui5sZa2LAaHnsviZdVOUZw4fvbnME=
 go.uber.org/automaxprocs v1.5.2/go.mod h1:eRbA25aqJrxAbsLO0xy5jVwPt7FQnRgjW+efnwa1WM0=
 go.uber.org/multierr v1.1.0 h1:HoEmRHQPVSqub6w2z2d2EOVs2fjyFRGyofhKuyDq0QI=
 go.uber.org/zap v1.9.1 h1:XCJQEf3W6eZaVwhRBof6ImoYGJSITeKWsyeh3HFu/5o=
@@ -782,6 +788,7 @@ golang.org/x/sys v0.0.0-20220128215802-99c3d69c2c27/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.7.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.10.0 h1:3R7pNqamzBraeqj/Tj8qt1aQ2HpmlC+Cx/qL/7hn4/c=
 golang.org/x/term v0.10.0/go.mod h1:lpqdcUyK/oCiQxvxVrppt5ggO2KCZ5QblwqPnfZ6d5o=
+golang.org/x/term v0.11.0 h1:F9tnn/DA/Im8nCwm+fX+1/eBwi4qFjRT++MhtVC4ZX0=
 golang.org/x/term v0.11.0/go.mod h1:zC9APTIj3jG3FdV/Ons+XE1riIZXG4aZ4GTHiPZJPIU=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
```

### prover/client/client.go
```diff
@@ -165,7 +165,7 @@ func (c *CoordinatorClient) GetTask(ctx context.Context, req *GetTaskRequest) (*
 }
 
 // SubmitProof sends a request to the coordinator to submit proof.
-func (c *CoordinatorClient) SubmitProof(ctx context.Context, req *SubmitProofRequest) error {
+func (c *CoordinatorClient) SubmitProof(ctx context.Context, req *SubmitProofRequest) (needDelete bool, err error) {
 	var result SubmitProofResponse
 
 	resp, err := c.client.R().
@@ -175,24 +175,24 @@ func (c *CoordinatorClient) SubmitProof(ctx context.Context, req *SubmitProofReq
 		Post("/coordinator/v1/submit_proof")
 
 	if err != nil {
-		return fmt.Errorf("submit proof request failed: %v", err)
+		return false, fmt.Errorf("submit proof request failed: %v", err)
 	}
 
 	if resp.StatusCode() != 200 {
-		return fmt.Errorf("failed to submit proof, status code: %v", resp.StatusCode())
+		return false, fmt.Errorf("failed to submit proof, status code: %v", resp.StatusCode())
 	}
 
 	if result.ErrCode == types.ErrJWTTokenExpired {
 		log.Info("JWT expired, attempting to re-login")
 		if err := c.Login(ctx); err != nil {
-			return fmt.Errorf("JWT expired, re-login failed: %v", err)
+			return false, fmt.Errorf("JWT expired, re-login failed: %v", err)
 		}
 		log.Info("re-login success")
 		return c.SubmitProof(ctx, req)
 	}
 	if result.ErrCode != types.Success {
-		return fmt.Errorf("error code: %v, error message: %v", result.ErrCode, result.ErrMsg)
+		return true, fmt.Errorf("error code: %v, error message: %v", result.ErrCode, result.ErrMsg)
 	}
 
-	return nil
+	return true, nil
 }
```

### prover/prover.go
```diff
@@ -321,14 +321,19 @@ func (r *Prover) submitProof(msg *message.ProofDetail) error {
 	}
 
 	// send the submit request
-	if err := r.coordinatorClient.SubmitProof(r.ctx, req); err != nil {
+	needDeleteTask, err := r.coordinatorClient.SubmitProof(r.ctx, req)
+	if needDeleteTask {
+		if deleteErr := r.stack.Delete(msg.ID); deleteErr != nil {
+			log.Error("prover stack pop failed", "task_type", msg.Type, "task_id", msg.ID, "err", deleteErr)
+		}
+	}
+
+	if err != nil {
 		return fmt.Errorf("error submitting proof: %v", err)
 	}
 
 	log.Info("proof submitted successfully", "task-id", msg.ID, "task-type", msg.Type, "task-status", msg.Status, "err", msg.Error)
-	if err := r.stack.Delete(msg.ID); err != nil {
-		log.Error("prover stack pop failed", "task_type", msg.Type, "task_id", msg.ID, "err", err)
-	}
+
 	return nil
 }
 
@@ -344,16 +349,20 @@ func (r *Prover) submitErr(task *store.ProvingTask, proofFailureType message.Pro
 	}
 
 	// send the submit request
-	if submitErr := r.coordinatorClient.SubmitProof(r.ctx, req); submitErr != nil {
+	needDeleteTask, submitErr := r.coordinatorClient.SubmitProof(r.ctx, req)
+	if needDeleteTask {
+		if deleteErr := r.stack.Delete(task.Task.ID); deleteErr != nil {
+			log.Error("prover stack pop failed", "task_type", task.Task.Type, "task_id", task.Task.ID, "err", deleteErr)
+		}
+	}
+
+	if submitErr != nil {
 		return fmt.Errorf("error submitting proof: %v", submitErr)
 	}
 
 	log.Info("proof submitted report failure successfully",
 		"task-id", task.Task.ID, "task-type", task.Task.Type,
 		"task-status", message.StatusProofError, "err", err)
-	if err = r.stack.Delete(task.Task.ID); err != nil {
-		log.Error("prover stack pop failed", "task_type", task.Task.Type, "task_id", task.Task.ID, "err", err)
-	}
 	return nil
 }
 
```
