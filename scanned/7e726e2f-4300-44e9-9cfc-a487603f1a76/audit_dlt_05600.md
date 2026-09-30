# [?] accounts/abi: fix panic when check event with log has empty or nil topics (#32503)

## Summary
Severity: Unknown
Chain: Ethereum
Component: ethereum/go-ethereum
Published: 2025-08-27
Source: https://github.com/ethereum/go-ethereum/commit/52ec2b5f47ca899a35df1bd9b03750dc2db6f2a9
Type: security-commit

## Details
accounts/abi: fix panic when check event with log has empty or nil topics (#32503)

When the log has empty or nil topics, the generated bindings code will
panic when accessing `log.Topics[0]`, add a check to avoid it.

## Patch
### accounts/abi/abigen/source2.go.tpl
```diff
@@ -183,7 +183,7 @@ var (
 		// Solidity: {{.Original.String}}
 		func ({{ decapitalise $contract.Type}} *{{$contract.Type}}) Unpack{{.Normalized.Name}}Event(log *types.Log) (*{{$contract.Type}}{{.Normalized.Name}}, error) {
 			event := "{{.Original.Name}}"
-			if log.Topics[0] != {{ decapitalise $contract.Type}}.abi.Events[event].ID {
+			if len(log.Topics) == 0 || log.Topics[0] != {{ decapitalise $contract.Type}}.abi.Events[event].ID {
 				return nil, errors.New("event signature mismatch")
 			}
 			out := new({{$contract.Type}}{{.Normalized.Name}})
```

### accounts/abi/abigen/testdata/v2/crowdsale.go.txt
```diff
@@ -360,7 +360,7 @@ func (CrowdsaleFundTransfer) ContractEventName() string {
 // Solidity: event FundTransfer(address backer, uint256 amount, bool isContribution)
 func (crowdsale *Crowdsale) UnpackFundTransferEvent(log *types.Log) (*CrowdsaleFundTransfer, error) {
 	event := "FundTransfer"
-	if log.Topics[0] != crowdsale.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != crowdsale.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(CrowdsaleFundTransfer)
```

### accounts/abi/abigen/testdata/v2/dao.go.txt
```diff
@@ -606,7 +606,7 @@ func (DAOChangeOfRules) ContractEventName() string {
 // Solidity: event ChangeOfRules(uint256 minimumQuorum, uint256 debatingPeriodInMinutes, int256 majorityMargin)
 func (dAO *DAO) UnpackChangeOfRulesEvent(log *types.Log) (*DAOChangeOfRules, error) {
 	event := "ChangeOfRules"
-	if log.Topics[0] != dAO.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != dAO.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(DAOChangeOfRules)
@@ -648,7 +648,7 @@ func (DAOMembershipChanged) ContractEventName() string {
 // Solidity: event MembershipChanged(address member, bool isMember)
 func (dAO *DAO) UnpackMembershipChangedEvent(log *types.Log) (*DAOMembershipChanged, error) {
 	event := "MembershipChanged"
-	if log.Topics[0] != dAO.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != dAO.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(DAOMembershipChanged)
@@ -692,7 +692,7 @@ func (DAOProposalAdded) ContractEventName() string {
 // Solidity: event ProposalAdded(uint256 proposalID, address recipient, uint256 amount, string description)
 func (dAO *DAO) UnpackProposalAddedEvent(log *types.Log) (*DAOProposalAdded, error) {
 	event := "ProposalAdded"
-	if log.Topics[0] != dAO.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != dAO.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(DAOProposalAdded)
@@ -736,7 +736,7 @@ func (DAOProposalTallied) ContractEventName() string {
 // Solidity: event ProposalTallied(uint256 proposalID, int256 result, uint256 quorum, bool active)
 func (dAO *DAO) UnpackProposalTalliedEvent(log *types.Log) (*DAOProposalTallied, error) {
 	event := "ProposalTallied"
-	if log.Topics[0] != dAO.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != dAO.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(DAOProposalTallied)
@@ -780,7 +780,7 @@ func (DAOVoted) ContractEventName() string {
 // Solidity: event Voted(uint256 proposalID, bool position, address voter, string justification)
 func (dAO *DAO) UnpackVotedEvent(log *types.Log) (*DAOVoted, error) {
 	event := "Voted"
-	if log.Topics[0] != dAO.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != dAO.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(DAOVoted)
```

### accounts/abi/abigen/testdata/v2/eventchecker.go.txt
```diff
@@ -72,7 +72,7 @@ func (EventCheckerDynamic) ContractEventName() string {
 // Solidity: event dynamic(string indexed idxStr, bytes indexed idxDat, string str, bytes dat)
 func (eventChecker *EventChecker) UnpackDynamicEvent(log *types.Log) (*EventCheckerDynamic, error) {
 	event := "dynamic"
-	if log.Topics[0] != eventChecker.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != eventChecker.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(EventCheckerDynamic)
@@ -112,7 +112,7 @@ func (EventCheckerEmpty) ContractEventName() string {
 // Solidity: event empty()
 func (eventChecker *EventChecker) UnpackEmptyEvent(log *types.Log) (*EventCheckerEmpty, error) {
 	event := "empty"
-	if log.Topics[0] != eventChecker.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != eventChecker.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(EventCheckerEmpty)
@@ -154,7 +154,7 @@ func (EventCheckerIndexed) ContractEventName() string {
 // Solidity: event indexed(address indexed addr, int256 indexed num)
 func (eventChecker *EventChecker) UnpackIndexedEvent(log *types.Log) (*EventCheckerIndexed, error) {
 	event := "indexed"
-	if log.Topics[0] != eventChecker.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != eventChecker.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(EventCheckerIndexed)
@@ -196,7 +196,7 @@ func (EventCheckerMixed) ContractEventName() string {
 // Solidity: event mixed(address indexed addr, int256 num)
 func (eventChecker *EventChecker) UnpackMixedEvent(log *types.Log) (*EventCheckerMixed, error) {
 	event := "mixed"
-	if log.Topics[0] != eventChecker.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != eventChecker.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(EventCheckerMixed)
@@ -238,7 +238,7 @@ func (EventCheckerUnnamed) ContractEventName() string {
 // Solidity: event unnamed(uint256 indexed arg0, uint256 indexed arg1)
 func (eventChecker *EventChecker) UnpackUnnamedEvent(log *types.Log) (*EventCheckerUnnamed, error) {
 	event := "unnamed"
-	if log.Topics[0] != eventChecker.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != eventChecker.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(EventCheckerUnnamed)
```

### accounts/abi/abigen/testdata/v2/nameconflict.go.txt
```diff
@@ -134,7 +134,7 @@ func (NameConflictLog) ContractEventName() string {
 // Solidity: event log(int256 msg, int256 _msg)
 func (nameConflict *NameConflict) UnpackLogEvent(log *types.Log) (*NameConflictLog, error) {
 	event := "log"
-	if log.Topics[0] != nameConflict.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != nameConflict.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(NameConflictLog)
```

### accounts/abi/abigen/testdata/v2/numericmethodname.go.txt
```diff
@@ -136,7 +136,7 @@ func (NumericMethodNameE1TestEvent) ContractEventName() string {
 // Solidity: event _1TestEvent(address _param)
 func (numericMethodName *NumericMethodName) UnpackE1TestEventEvent(log *types.Log) (*NumericMethodNameE1TestEvent, error) {
 	event := "_1TestEvent"
-	if log.Topics[0] != numericMethodName.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != numericMethodName.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(NumericMethodNameE1TestEvent)
```

### accounts/abi/abigen/testdata/v2/overload.go.txt
```diff
@@ -114,7 +114,7 @@ func (OverloadBar) ContractEventName() string {
 // Solidity: event bar(uint256 i)
 func (overload *Overload) UnpackBarEvent(log *types.Log) (*OverloadBar, error) {
 	event := "bar"
-	if log.Topics[0] != overload.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != overload.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(OverloadBar)
@@ -156,7 +156,7 @@ func (OverloadBar0) ContractEventName() string {
 // Solidity: event bar(uint256 i, uint256 j)
 func (overload *Overload) UnpackBar0Event(log *types.Log) (*OverloadBar0, error) {
 	event := "bar0"
-	if log.Topics[0] != overload.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != overload.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(OverloadBar0)
```

### accounts/abi/abigen/testdata/v2/token.go.txt
```diff
@@ -386,7 +386,7 @@ func (TokenTransfer) ContractEventName() string {
 // Solidity: event Transfer(address indexed from, address indexed to, uint256 value)
 func (token *Token) UnpackTransferEvent(log *types.Log) (*TokenTransfer, error) {
 	event := "Transfer"
-	if log.Topics[0] != token.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != token.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(TokenTransfer)
```

### accounts/abi/abigen/testdata/v2/tuple.go.txt
```diff
@@ -193,7 +193,7 @@ func (TupleTupleEvent) ContractEventName() string {
 // Solidity: event TupleEvent((uint256,uint256[],(uint256,uint256)[]) a, (uint256,uint256)[2][] b, (uint256,uint256)[][2] c, (uint256,uint256[],(uint256,uint256)[])[] d, uint256[] e)
 func (tuple *Tuple) UnpackTupleEventEvent(log *types.Log) (*TupleTupleEvent, error) {
 	event := "TupleEvent"
-	if log.Topics[0] != tuple.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != tuple.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(TupleTupleEvent)
@@ -234,7 +234,7 @@ func (TupleTupleEvent2) ContractEventName() string {
 // Solidity: event TupleEvent2((uint8,uint8)[] arg0)
 func (tuple *Tuple) UnpackTupleEvent2Event(log *types.Log) (*TupleTupleEvent2, error) {
 	event := "TupleEvent2"
-	if log.Topics[0] != tuple.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != tuple.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(TupleTupleEvent2)
```

### accounts/abi/bind/v2/internal/contracts/db/bindings.go
```diff
@@ -276,7 +276,7 @@ func (DBInsert) ContractEventName() string {
 // Solidity: event Insert(uint256 key, uint256 value, uint256 length)
 func (dB *DB) UnpackInsertEvent(log *types.Log) (*DBInsert, error) {
 	event := "Insert"
-	if log.Topics[0] != dB.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != dB.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(DBInsert)
@@ -318,7 +318,7 @@ func (DBKeyedInsert) ContractEventName() string {
 // Solidity: event KeyedInsert(uint256 indexed key, uint256 value)
 func (dB *DB) UnpackKeyedInsertEvent(log *types.Log) (*DBKeyedInsert, error) {
 	event := "KeyedInsert"
-	if log.Topics[0] != dB.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != dB.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(DBKeyedInsert)
```

### accounts/abi/bind/v2/internal/contracts/events/bindings.go
```diff
@@ -115,7 +115,7 @@ func (CBasic1) ContractEventName() string {
 // Solidity: event basic1(uint256 indexed id, uint256 data)
 func (c *C) UnpackBasic1Event(log *types.Log) (*CBasic1, error) {
 	event := "basic1"
-	if log.Topics[0] != c.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != c.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(CBasic1)
@@ -157,7 +157,7 @@ func (CBasic2) ContractEventName() string {
 // Solidity: event basic2(bool indexed flag, uint256 data)
 func (c *C) UnpackBasic2Event(log *types.Log) (*CBasic2, error) {
 	event := "basic2"
-	if log.Topics[0] != c.abi.Events[event].ID {
+	if len(log.Topics) == 0 || log.Topics[0] != c.abi.Events[event].ID {
 		return nil, errors.New("event signature mismatch")
 	}
 	out := new(CBasic2)
```

### accounts/abi/bind/v2/lib_test.go
```diff
@@ -367,3 +367,28 @@ func TestErrors(t *testing.T) {
 		t.Fatalf("bad unpacked error result: expected Arg4 to be false.  got true")
 	}
 }
+
+func TestEventUnpackEmptyTopics(t *testing.T) {
+	c := events.NewC()
+
+	for _, log := range []*types.Log{
+		{Topics: []common.Hash{}},
+		{Topics: nil},
+	} {
+		_, err := c.UnpackBasic1Event(log)
+		if err == nil {
+			t.Fatal("expected error when unpacking event with empty topics, got nil")
+		}
+		if err.Error() != "event signature mismatch" {
+			t.Fatalf("expected 'event signature mismatch' error, got: %v", err)
+		}
+
+		_, err = c.UnpackBasic2Event(log)
+		if err == nil {
+			t.Fatal("expected error when unpacking event with empty topics, got nil")
+		}
+		if err.Error() != "event signature mismatch" {
+			t.Fatalf("expected 'event signature mismatch' error, got: %v", err)
+		}
+	}
+}
```
