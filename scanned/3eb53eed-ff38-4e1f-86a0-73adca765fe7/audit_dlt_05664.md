# [?] prevent panic by returning on connection error (#14602)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2024-11-04
Source: https://github.com/OffchainLabs/prysm/commit/bcb4155523c0707b4828dc6cda008c78319ec2fc
Type: security-commit

## Details
prevent panic by returning on connection error (#14602)

* prevent panic by returning on connection error

* add test

* don't close eventschannel on error

---------

Co-authored-by: Sammy Rosso <15244892+saolyn@users.noreply.github.com>
Co-authored-by: james-prysm <90280386+james-prysm@users.noreply.github.com>

## Patch
### CHANGELOG.md
```diff
@@ -45,6 +45,7 @@ The format is based on Keep a Changelog, and this project adheres to Semantic Ve
 - Changed the signature of `ProcessPayload`.
 - Only Build the Protobuf state once during serialization.
 - Capella blocks are execution.
+- Fixed panic when http request to subscribe to event stream fails.
 
 ### Deprecated
 
```

### api/client/event/event_stream.go
```diff
@@ -93,6 +93,7 @@ func (h *EventStream) Subscribe(eventsChannel chan<- *Event) {
 			EventType: EventConnectionError,
 			Data:      []byte(errors.Wrap(err, client.ErrConnectionIssue.Error()).Error()),
 		}
+		return
 	}
 
 	defer func() {
```

### api/client/event/event_stream_test.go
```diff
@@ -40,7 +40,7 @@ func TestNewEventStream(t *testing.T) {
 
 func TestEventStream(t *testing.T) {
 	mux := http.NewServeMux()
-	mux.HandleFunc("/eth/v1/events", func(w http.ResponseWriter, r *http.Request) {
+	mux.HandleFunc("/eth/v1/events", func(w http.ResponseWriter, _ *http.Request) {
 		flusher, ok := w.(http.Flusher)
 		require.Equal(t, true, ok)
 		for i := 1; i <= 3; i++ {
@@ -79,3 +79,23 @@ func TestEventStream(t *testing.T) {
 		}
 	}
 }
+
+func TestEventStreamRequestError(t *testing.T) {
+	topics := []string{"head"}
+	eventsChannel := make(chan *Event, 1)
+	ctx, cancel := context.WithCancel(context.Background())
+	defer cancel()
+
+	// use valid url that will result in failed request with nil body
+	stream, err := NewEventStream(ctx, http.DefaultClient, "http://badhost:1234", topics)
+	require.NoError(t, err)
+
+	// error will happen when request is made, should be received over events channel
+	go stream.Subscribe(eventsChannel)
+
+	event := <-eventsChannel
+	if event.EventType != EventConnectionError {
+		t.Errorf("Expected event type %q, got %q", EventConnectionError, event.EventType)
+	}
+
+}
```
