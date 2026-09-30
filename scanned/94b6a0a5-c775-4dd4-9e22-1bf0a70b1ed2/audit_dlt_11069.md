# [?] fix: roller reward dispatch and proof resubmission DoS (#100)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2022-11-17
Source: https://github.com/scroll-tech/scroll/commit/0b5f931212b1d9feac7e1c35a26ed51ab1023164
Type: security-commit

## Details
fix: roller reward dispatch and proof resubmission DoS (#100)

Co-authored-by: colinlyguo <colinlyguo@gmail.com>
Co-authored-by: HAOYUatHZ <37070449+HAOYUatHZ@users.noreply.github.com>

## Patch
### Makefile
```diff
@@ -27,7 +27,7 @@ update: ## update dependencies
 
 dev_docker: ## build docker images for development/testing usages
 	docker build -t scroll_l1geth ./common/docker/l1geth/
-	docker build -t scroll_l2geth ./common/docker/l2geth/.
+	docker build -t scroll_l2geth ./common/docker/l2geth/
 
 clean: ## Empty out the bin folder
 	@rm -rf build/bin
```

### coordinator/api.go
```diff
@@ -47,7 +47,7 @@ func (m *Manager) ListRollers() ([]*RollerInfo, error) {
 			PublicKey: pk,
 		}
 		for id, sess := range m.sessions {
-			if sess.rollers[pk] {
+			if _, ok := sess.rollers[pk]; ok {
 				info.ActiveSessionStartTime = sess.startTime
 				info.ActiveSession = id
 				break
```

### coordinator/manager.go
```diff
@@ -27,19 +27,32 @@ const (
 	proofAndPkBufferSize = 10
 )
 
+type rollerStatus int32
+
+const (
+	rollerAssigned rollerStatus = iota
+	rollerProofValid
+	rollerProofInvalid
+)
+
+type rollerProofStatus struct {
+	pk     string
+	status rollerStatus
+}
+
 // Contains all the information on an ongoing proof generation session.
 type session struct {
 	// session id
 	id uint64
 	// A list of all participating rollers and if they finished proof generation for this session.
 	// The map key is a hexadecimal encoding of the roller public key, as byte slices
 	// can not be compared explicitly.
-	rollers      map[string]bool
+	rollers      map[string]rollerStatus
 	roller_names map[string]string
 	// session start time
 	startTime time.Time
 	// finish channel is used to pass the public key of the rollers who finished proving process.
-	finishChan chan string
+	finishChan chan rollerProofStatus
 }
 
 // Manager is responsible for maintaining connections with active rollers,
@@ -232,6 +245,7 @@ func (m *Manager) HandleMessage(pk string, payload []byte) error {
 // db/unmarshal errors will not because they are errors on the business logic side.
 func (m *Manager) HandleZkProof(pk string, payload []byte) error {
 	var dbErr error
+	var success bool
 
 	msg := &message.ProofMsg{}
 	if err := json.Unmarshal(payload, msg); err != nil {
@@ -250,21 +264,35 @@ func (m *Manager) HandleZkProof(pk string, payload []byte) error {
 	proofTimeSec := uint64(time.Since(s.startTime).Seconds())
 
 	// Ensure this roller is eligible to participate in the session.
-	if _, ok = s.rollers[pk]; !ok {
+	if status, ok := s.rollers[pk]; !ok {
 		return fmt.Errorf("roller %s is not eligible to partake in proof session %v", pk, msg.ID)
+	} else if status == rollerProofValid {
+		// In order to prevent DoS attacks, it is forbidden to repeatedly submit valid proofs.
+		// TODO: Defend invalid proof resubmissions by one of the following two methods:
+		// (i) slash the roller for each submission of invalid proof
+		// (ii) set the maximum failure retry times
+		log.Warn("roller has already submitted valid proof in proof session", "roller", pk, "proof id", msg.ID)
+		return nil
 	}
 	log.Info("Received zk proof", "proof id", msg.ID)
 
 	defer func() {
-		// notify the session that the roller finishes the proving process
-		s.finishChan <- pk
 		// TODO: maybe we should use db tx for the whole process?
 		// Roll back current proof's status.
 		if dbErr != nil {
 			if err := m.orm.UpdateBlockStatus(msg.ID, orm.BlockUnassigned); err != nil {
 				log.Error("fail to reset block_status as Unassigned", "msg.ID", msg.ID)
 			}
 		}
+		// set proof status
+		var status rollerStatus
+		if success && dbErr == nil {
+			status = rollerProofValid
+		} else {
+			status = rollerProofInvalid
+		}
+		// notify the session that the roller finishes the proving process
+		s.finishChan <- rollerProofStatus{pk, status}
 	}()
 
 	if msg.Status != message.StatusOk {
@@ -287,7 +315,6 @@ func (m *Manager) HandleZkProof(pk string, payload []byte) error {
 		return dbErr
 	}
 
-	var success bool
 	if m.verifier != nil {
 		blockResults, err := m.orm.GetBlockResults(map[string]interface{}{"number": msg.ID})
 		if len(blockResults) == 0 {
@@ -347,17 +374,17 @@ func (m *Manager) CollectProofs(id uint64, s session) {
 			}()
 
 			// Pick a random winner.
-			// First, round up the keys that actually sent in a proof.
+			// First, round up the keys that actually sent in a valid proof.
 			var participatingRollers []string
-			for pk, finished := range s.rollers {
-				if finished {
+			for pk, status := range s.rollers {
+				if status == rollerProofValid {
 					participatingRollers = append(participatingRollers, pk)
 				}
 			}
 			// Ensure we got at least one proof before selecting a winner.
 			if len(participatingRollers) == 0 {
 				// record failed session.
-				errMsg := "proof generation session ended without receiving any proofs"
+				errMsg := "proof generation session ended without receiving any valid proofs"
 				m.addFailedSession(&s, errMsg)
 				log.Warn(errMsg, "session id", id)
 				// Set status as skipped.
@@ -375,9 +402,9 @@ func (m *Manager) CollectProofs(id uint64, s session) {
 			_ = participatingRollers[randIndex]
 			// TODO: reward winner
 			return
-		case pk := <-s.finishChan:
+		case ret := <-s.finishChan:
 			m.mu.Lock()
-			s.rollers[pk] = true
+			s.rollers[ret.pk] = ret.status
 			m.mu.Unlock()
 		}
 	}
@@ -439,14 +466,14 @@ func (m *Manager) StartProofGenerationSession(trace *types.BlockResult) bool {
 
 	s := session{
 		id: id,
-		rollers: map[string]bool{
-			pk: false,
+		rollers: map[string]rollerStatus{
+			pk: rollerAssigned,
 		},
 		roller_names: map[string]string{
 			pk: roller.AuthMsg.Identity.Name,
 		},
 		startTime:  time.Now(),
-		finishChan: make(chan string, proofAndPkBufferSize),
+		finishChan: make(chan rollerProofStatus, proofAndPkBufferSize),
 	}
 
 	// Create a proof generation session.
@@ -494,8 +521,8 @@ func (m *Manager) IsRollerIdle(hexPk string) bool {
 	// We need to iterate over all sessions because finished sessions will be deleted until the
 	// timeout. So a busy roller could be marked as idle in a finished session.
 	for _, sess := range m.sessions {
-		for pk, finished := range sess.rollers {
-			if pk == hexPk && !finished {
+		for pk, status := range sess.rollers {
+			if pk == hexPk && status == rollerAssigned {
 				return false
 			}
 		}
```
