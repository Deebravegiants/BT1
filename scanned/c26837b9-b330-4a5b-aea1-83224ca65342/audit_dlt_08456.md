# [?] fix(api/gateway): Handle err from tx properly to avoid panic (#2393)

## Summary
Severity: Unknown
Chain: Celestia
Component: celestiaorg/celestia-node
Published: 2023-06-23
Source: https://github.com/celestiaorg/celestia-node/commit/8b28ad799688b5cbfe22dc2b4449f15c248badba
Type: security-commit

## Details
fix(api/gateway): Handle err from tx properly to avoid panic (#2393)

Fixes a panic that can occur if txResp is nil and also returns actual
error in the case of nil txResp.

Reported by @tuxcanfly

## Patch
### api/gateway/state.go
```diff
@@ -150,10 +150,15 @@ func (h *Handler) handleSubmitPFB(w http.ResponseWriter, r *http.Request) {
 	}
 
 	// perform request
-	txResp, txerr := h.state.SubmitPayForBlob(r.Context(), fee, req.GasLimit, []*blob.Blob{constructedBlob})
-	if txerr != nil && txResp == nil {
-		// no tx data to return
-		writeError(w, http.StatusInternalServerError, submitPFBEndpoint, err)
+	txResp, err := h.state.SubmitPayForBlob(r.Context(), fee, req.GasLimit, []*blob.Blob{constructedBlob})
+	if err != nil {
+		if txResp == nil {
+			// no tx data to return
+			writeError(w, http.StatusBadRequest, submitPFBEndpoint, err)
+			return
+		}
+		// if error returned, change status from 200 to 206
+		w.WriteHeader(http.StatusPartialContent)
 	}
 
 	bs, err := json.Marshal(&txResp)
@@ -162,10 +167,6 @@ func (h *Handler) handleSubmitPFB(w http.ResponseWriter, r *http.Request) {
 		return
 	}
 
-	// if error returned, change status from 200 to 206
-	if txerr != nil {
-		w.WriteHeader(http.StatusPartialContent)
-	}
 	_, err = w.Write(bs)
 	if err != nil {
 		log.Errorw("writing response", "endpoint", submitPFBEndpoint, "err", err)
```
