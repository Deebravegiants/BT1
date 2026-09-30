# [?] Fix power overflow issues when checking for a potential strong quorum (#590)

## Summary
Severity: Unknown
Chain: Filecoin
Component: filecoin-project/go-f3
Published: 2024-08-26
Source: https://github.com/filecoin-project/go-f3/commit/f85100a1004339086dd5520a27fe5568707e36b1
Type: security-commit

## Details
Fix power overflow issues when checking for a potential strong quorum (#590)

* Use int64 for power calculations, not uint16

Fixes an overflow when computing the maximum amount of support a
proposal could have had. There's no reason to use uint16 here anyways,
even if power values are guaranteed to fit.

* Limit power to the max available in `CouldReachStrongQuorumFor`

We're intentionally double-counting adversary power here, so should
handle the case where our power sums to over the total.

## Patch
### certs/certs.go
```diff
@@ -150,7 +150,7 @@ func verifyFinalityCertificateSignature(verifier gpbft.Verifier, powerTable gpbf
 	}
 
 	signers := make([]gpbft.PubKey, 0, len(powerTable))
-	var signerPowers uint16
+	var signerPowers int64
 	if err := cert.Signers.ForEach(func(i uint64) error {
 		if i >= uint64(len(powerTable)) {
 			return fmt.Errorf(
```

### certs/certs_test.go
```diff
@@ -367,7 +367,7 @@ func TestBadFinalityCertificates(t *testing.T) {
 		}))
 		scaledPowerTable, totalPower, err := powerTableCpy.Scaled()
 		require.NoError(t, err)
-		var activePower uint16
+		var activePower int64
 		require.NoError(t, certificate.Signers.ForEach(func(i uint64) error {
 			activePower += scaledPowerTable[i]
 			return nil
```

### gpbft/gpbft.go
```diff
@@ -979,7 +979,7 @@ type quorumState struct {
 	// Set of senders from which a message has been received.
 	senders map[ActorID]struct{}
 	// Total power of all distinct senders from which some chain has been received so far.
-	sendersTotalPower uint16
+	sendersTotalPower int64
 	// The power supporting each chain so far.
 	chainSupport map[ChainKey]chainSupport
 	// Table of senders' power.
@@ -991,7 +991,7 @@ type quorumState struct {
 // A chain value and the total power supporting it
 type chainSupport struct {
 	chain           ECChain
-	power           uint16
+	power           int64
 	signatures      map[ActorID][]byte
 	hasStrongQuorum bool
 }
@@ -1034,7 +1034,7 @@ func (q *quorumState) ReceiveEachPrefix(sender ActorID, values ECChain) {
 
 // Adds sender's power to total the first time a value is received from them.
 // Returns the sender's power, and whether this was the first invocation for this sender.
-func (q *quorumState) receiveSender(sender ActorID) (uint16, bool) {
+func (q *quorumState) receiveSender(sender ActorID) (int64, bool) {
 	if _, found := q.senders[sender]; found {
 		return 0, false
 	}
@@ -1045,7 +1045,7 @@ func (q *quorumState) receiveSender(sender ActorID) (uint16, bool) {
 }
 
 // Receives a chain from a sender.
-func (q *quorumState) receiveInner(sender ActorID, value ECChain, power uint16, signature []byte) {
+func (q *quorumState) receiveInner(sender ActorID, value ECChain, power int64, signature []byte) {
 	key := value.Key()
 	candidate, ok := q.chainSupport[key]
 	if !ok {
@@ -1110,19 +1110,22 @@ func (q *quorumState) HasStrongQuorumFor(key ChainKey) bool {
 // representing an equivocating adversary. This is appropriate for testing whether
 // any other participant could have observed a strong quorum in the presence of such adversary.
 func (q *quorumState) CouldReachStrongQuorumFor(key ChainKey, withAdversary bool) bool {
-	var supportingPower uint16
+	var supportingPower int64
 	if supportForChain, found := q.chainSupport[key]; found {
 		supportingPower = supportForChain.power
 	}
 	// A strong quorum is only feasible when the total support for the given chain,
 	// combined with the aggregate power of not yet voted participants, exceeds ⅔ of
 	// total power.
 	unvotedPower := q.powerTable.ScaledTotal - q.sendersTotalPower
-	adversaryPower := uint16(0)
+	adversaryPower := int64(0)
 	if withAdversary {
+		// Account for the fact that the adversary may have double-voted here.
 		adversaryPower = q.powerTable.ScaledTotal / 3
 	}
-	possibleSupport := supportingPower + unvotedPower + adversaryPower
+	// We're double-counting adversary power, so we need to cap the power at the total available
+	// power.
+	possibleSupport := min(supportingPower+unvotedPower+adversaryPower, q.powerTable.ScaledTotal)
 	return IsStrongQuorum(possibleSupport, q.powerTable.ScaledTotal)
 }
 
@@ -1172,7 +1175,7 @@ func (q *quorumState) FindStrongQuorumFor(key ChainKey) (QuorumResult, bool) {
 	// Accumulate signers and signatures until they reach a strong quorum.
 	signatures := make([][]byte, 0, len(chainSupport.signatures))
 	pubkeys := make([]PubKey, 0, len(signatures))
-	var justificationPower uint16
+	var justificationPower int64
 	for i, idx := range signers {
 		if idx >= len(q.powerTable.Entries) {
 			panic(fmt.Sprintf("invalid signer index: %d for %d entries", idx, len(q.powerTable.Entries)))
@@ -1427,7 +1430,7 @@ func findFirstPrefixOf(preferred ECChain, candidates []ECChain) ECChain {
 	return preferred.BaseChain()
 }
 
-func divCeil(a, b uint32) uint32 {
+func divCeil(a, b int64) int64 {
 	quo := a / b
 	rem := a % b
 	if rem != 0 {
@@ -1437,15 +1440,15 @@ func divCeil(a, b uint32) uint32 {
 }
 
 // Check whether a portion of storage power is a strong quorum of the total
-func IsStrongQuorum(part uint16, whole uint16) bool {
-	// uint32 because 2 * whole exceeds uint16
-	return uint32(part) >= divCeil(2*uint32(whole), 3)
+func IsStrongQuorum(part int64, whole int64) bool {
+	// uint32 because 2 * whole exceeds int64
+	return part >= divCeil(2*whole, 3)
 }
 
 // Check whether a portion of storage power is a weak quorum of the total
-func hasWeakQuorum(part, whole uint16) bool {
+func hasWeakQuorum(part, whole int64) bool {
 	// Must be strictly greater than 1/3. Otherwise, there could be a strong quorum.
-	return uint32(part) > divCeil(uint32(whole), 3)
+	return part > divCeil(whole, 3)
 }
 
 // Tests whether lhs is equal to or greater than rhs.
```

### gpbft/message_builder.go
```diff
@@ -19,7 +19,7 @@ type MessageBuilder struct {
 }
 
 type powerTableAccessor interface {
-	Get(ActorID) (uint16, PubKey)
+	Get(ActorID) (int64, PubKey)
 }
 
 type SignerWithMarshaler interface {
```

### gpbft/participant.go
```diff
@@ -332,7 +332,7 @@ func (p *Participant) validateJustification(msg *GMessage, comt *committee) erro
 	}
 
 	// Check justification power and signature.
-	var justificationPower uint16
+	var justificationPower int64
 	signers := make([]PubKey, 0)
 	if err := msg.Justification.Signers.ForEach(func(bit uint64) error {
 		if int(bit) >= len(comt.power.Entries) {
```

### gpbft/powertable.go
```diff
@@ -27,10 +27,10 @@ type PowerEntries []PowerEntry
 // Entries is the reverse mapping to a PowerEntry.
 type PowerTable struct {
 	Entries     PowerEntries // Slice to maintain the order. Meant to be maintained in order in order by (Power descending, ID ascending)
-	ScaledPower []uint16
+	ScaledPower []int64
 	Lookup      map[ActorID]int // Maps ActorID to the index of the associated entry in Entries
 	Total       StoragePower
-	ScaledTotal uint16
+	ScaledTotal int64
 }
 
 func (p *PowerEntry) Equal(o *PowerEntry) bool {
@@ -76,7 +76,7 @@ func (p PowerEntries) Swap(i, j int) {
 	p[i], p[j] = p[j], p[i]
 }
 
-func (p PowerEntries) Scaled() (scaled []uint16, total uint16, err error) {
+func (p PowerEntries) Scaled() (scaled []int64, total int64, err error) {
 	totalUnscaled := big.Zero()
 	for i := range p {
 		pwr := p[i].Power
@@ -85,7 +85,7 @@ func (p PowerEntries) Scaled() (scaled []uint16, total uint16, err error) {
 		}
 		totalUnscaled = big.Add(totalUnscaled, pwr)
 	}
-	scaled = make([]uint16, len(p))
+	scaled = make([]int64, len(p))
 	for i := range p {
 		p, err := scalePower(p[i].Power, totalUnscaled)
 		if err != nil {
@@ -148,7 +148,7 @@ func (p *PowerTable) rescale() error {
 
 // Get retrieves the scaled power, unscaled StoragePower and PubKey for the given id, if present in
 // the table. Otherwise, returns 0/nil.
-func (p *PowerTable) Get(id ActorID) (uint16, PubKey) {
+func (p *PowerTable) Get(id ActorID) (int64, PubKey) {
 	if index, ok := p.Lookup[id]; ok {
 		key := p.Entries[index].PubKey
 		scaledPower := p.ScaledPower[index]
@@ -213,7 +213,7 @@ func (p *PowerTable) Validate() error {
 		return errors.New("inconsistent entries and scaled power")
 	}
 	total := NewStoragePower(0)
-	totalScaled := 0 // int instead of uint16 to detect overflow
+	totalScaled := 0 // int instead of int64 to detect overflow
 	var previous *PowerEntry
 	for index, entry := range p.Entries {
 		if lookupIndex, found := p.Lookup[entry.ID]; !found || index != lookupIndex {
@@ -250,13 +250,13 @@ func (p *PowerTable) Validate() error {
 	return nil
 }
 
-func scalePower(power, total StoragePower) (uint16, error) {
+func scalePower(power, total StoragePower) (int64, error) {
 	const maxPower = 0xffff
 	if total.LessThan(power) {
 		return 0, fmt.Errorf("total power %d is less than the power of a single participant %d", total, power)
 	}
 	scaled := big.NewInt(maxPower)
 	scaled = big.Mul(scaled, power)
 	scaled = big.Div(scaled, total)
-	return uint16(scaled.Uint64()), nil
+	return scaled.Int64(), nil
 }
```

### gpbft/ticket_quality.go
```diff
@@ -19,7 +19,7 @@ import (
 // This ends up being `-log(ticket) / power` where ticket is [0, 1).
 // We additionally use log-base-2 instead of natural logarithm as it is easier to implement,
 // and it is just a linear factor on all tickets, meaning it does not influence their ordering.
-func ComputeTicketQuality(ticket []byte, power uint16) float64 {
+func ComputeTicketQuality(ticket []byte, power int64) float64 {
 	// we could use Blake2b-128 but 256 is more common and more widely supported
 	ticketHash := blake2b.Sum256(ticket)
 	quality := linearToExpDist(ticketHash[:16])
```

### sim/justification.go
```diff
@@ -37,7 +37,7 @@ func MakeJustification(backend signing.Backend, nn gpbft.NetworkName, chain gpbf
 	msg := backend.MarshalPayloadForSigning(nn, &payload)
 	signers := rand.Perm(len(powerTable))
 	signersBitfield := bitfield.New()
-	var signingPower uint16
+	var signingPower int64
 
 	type vote struct {
 		index int
```
