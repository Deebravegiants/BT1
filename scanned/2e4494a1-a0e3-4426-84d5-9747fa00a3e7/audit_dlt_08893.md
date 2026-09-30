# [?] fix(consensus): do not panic on stream type mismatch

## Summary
Severity: Unknown
Chain: Starknet
Component: software-mansion/pathfinder
Published: 2026-05-26
Source: https://github.com/software-mansion/pathfinder/commit/199fc2e8abfe58aa02ccdaba5a8877a48f154718
Type: security-commit

## Details
fix(consensus): do not panic on stream type mismatch

## Patch
### crates/p2p/src/consensus.rs
```diff
@@ -134,9 +134,9 @@ impl ActiveStream {
     /// messages.
     const TTL: Duration = Duration::from_secs(30);
 
-    fn new_incoming() -> Self {
+    fn new_incoming(source: PeerId) -> Self {
         Self {
-            state: StreamState::new_incoming(),
+            state: StreamState::new_incoming(source),
             last_active_at: Instant::now(),
         }
     }
@@ -154,6 +154,10 @@ impl ActiveStream {
 }
 
 /// Create a new outgoing proposal stream message.
+///
+/// If an incoming stream already exists for the given height and round, it is
+/// replaced by a fresh outgoing stream. We favor consensus engine commands in
+/// this way to prevent malicious peers from suppressing our proposals.
 pub fn create_outgoing_proposal_message(
     state: &mut State,
     height_and_round: HeightAndRound,
@@ -167,14 +171,23 @@ pub fn create_outgoing_proposal_message(
     let stream = state
         .active_streams
         .entry(height_and_round)
-        .and_modify(|e| e.last_active_at = Instant::now())
+        .and_modify(|stream| stream.last_active_at = Instant::now())
         .or_insert_with(|| {
             evict = true;
             ActiveStream::new_outgoing()
         });
 
+    // Always favor engine command over peer messages.
+    if let StreamState::Incoming(incoming) = &stream.state {
+        tracing::warn!(
+            %height_and_round,
+            source = %incoming.source,
+            "Replacing active incoming stream with outgoing proposal stream"
+        );
+        stream.state = StreamState::new_outgoing();
+    }
     let StreamState::Outgoing(stream_state) = &mut stream.state else {
-        panic!("Expected Outgoing stream state")
+        unreachable!("stream state set to outgoing");
     };
 
     let message_id = stream_state.last_sent_message_id.map_or(0, |id| id + 1);
@@ -213,52 +226,61 @@ pub fn create_outgoing_proposal_message(
 }
 
 /// Handle an incoming proposal message.
+///
+/// Returns `None` if there is already an outgoing stream for the given height
+/// and round (favoring engine commands over peer messages) or if the proposal
+/// isn't valid.
 pub fn handle_incoming_proposal_message(
     state: &mut State,
     message: StreamMessage<ProposalPart>,
     propagation_source: PeerId,
-) -> Vec<Event> {
+) -> Option<Vec<Event>> {
     let stream_id = message.stream_id;
     // Evict only when inserting a new stream.
     let mut evict = false;
 
     // Get or create stream state for this (height, round)
-    let stream = state
-        .active_streams
-        .entry(stream_id)
-        .and_modify(|e| e.last_active_at = Instant::now())
-        .or_insert_with(|| {
-            evict = true;
-            ActiveStream::new_incoming()
-        });
+    let stream = state.active_streams.entry(stream_id).or_insert_with(|| {
+        evict = true;
+        ActiveStream::new_incoming(propagation_source)
+    });
 
+    // Always favor engine command over peer messages.
     let StreamState::Incoming(stream_state) = &mut stream.state else {
-        panic!("Expected Incoming stream state")
+        tracing::warn!(
+            height_and_round = %stream_id,
+            source = %propagation_source,
+            "Ignoring incoming proposal message for active outgoing stream"
+        );
+        return None;
     };
 
     // Discard invalid messages
     if let Some(fin_id) = stream_state.fin_message_id {
         if message.message_id >= fin_id {
-            return vec![];
+            return None;
         }
     }
 
+    // Refresh activity marker only on valid messages.
+    stream.last_active_at = Instant::now();
+
     // Handle "Fin" message
     if let StreamMessageBody::Fin = message.message {
         stream_state.fin_message_id = Some(message.message_id);
         // Remove messages after the Fin message
         stream_state
             .received_messages
             .retain(|id, _| id < &message.message_id);
-        return vec![];
+        return Some(vec![]);
     }
 
     // Buffer out of order messages
     if message.message_id != stream_state.next_message_id {
         stream_state
             .received_messages
             .insert(message.message_id, message);
-        return vec![];
+        return Some(vec![]);
     }
 
     // Process this message (it's in order)
@@ -291,7 +313,7 @@ pub fn handle_incoming_proposal_message(
         state.active_streams.retain(|_, s| s.is_active());
     }
 
-    events
+    Some(events)
 }
 
 #[cfg(test)]
@@ -425,7 +447,8 @@ mod tests {
         };
 
         // Handle the message
-        let events = handle_incoming_proposal_message(&mut state, message, PeerId::random());
+        let events =
+            handle_incoming_proposal_message(&mut state, message, PeerId::random()).unwrap();
 
         // Verify state was updated
         let stream = state.active_streams.get(&height_and_round).unwrap();
@@ -468,6 +491,78 @@ mod tests {
         assert!(stream.is_active());
     }
 
+    #[test]
+    fn outgoing_proposal_message_replaces_existing_incoming_stream() {
+        let mut state = State::new();
+        let height_and_round: HeightAndRound = (1, 2).into();
+
+        let incoming_proposal = create_proposal_stream(1, 2, 100).1[0].clone();
+        let incoming_message = StreamMessage {
+            stream_id: height_and_round,
+            message_id: 0,
+            message: StreamMessageBody::Content(incoming_proposal),
+        };
+        handle_incoming_proposal_message(&mut state, incoming_message, PeerId::random()).unwrap();
+
+        let stream = state.active_streams.get(&height_and_round).unwrap();
+        let StreamState::Incoming(_) = &stream.state else {
+            panic!("Expected incoming stream state");
+        };
+
+        let outgoing_proposal = create_proposal_stream(1, 2, 200).1[0].clone();
+        let messages = create_outgoing_proposal_message(
+            &mut state,
+            height_and_round,
+            outgoing_proposal.clone(),
+        );
+
+        assert_eq!(messages.len(), 1);
+        assert_eq!(messages[0].message_id, 0);
+
+        let stream = state.active_streams.get(&height_and_round).unwrap();
+        let StreamState::Outgoing(outgoing_state) = &stream.state else {
+            panic!("Expected outgoing stream state");
+        };
+
+        assert_eq!(outgoing_state.last_sent_message_id, Some(0));
+        assert_eq!(
+            outgoing_state.sent_messages.get(&0),
+            Some(&outgoing_proposal)
+        );
+    }
+
+    #[test]
+    fn incoming_proposal_message_is_ignored_when_outgoing_stream_exists() {
+        let mut state = State::new();
+        let height_and_round: HeightAndRound = (1, 2).into();
+        let outgoing_proposal = create_proposal_stream(1, 2, 100).1[0].clone();
+
+        create_outgoing_proposal_message(&mut state, height_and_round, outgoing_proposal.clone());
+
+        let incoming_proposal = create_proposal_stream(1, 2, 200).1[0].clone();
+        let incoming_message = StreamMessage {
+            stream_id: height_and_round,
+            message_id: 0,
+            message: StreamMessageBody::Content(incoming_proposal),
+        };
+
+        assert!(
+            handle_incoming_proposal_message(&mut state, incoming_message, PeerId::random())
+                .is_none()
+        );
+
+        let stream = state.active_streams.get(&height_and_round).unwrap();
+        let StreamState::Outgoing(outgoing_state) = &stream.state else {
+            panic!("Expected outgoing stream state");
+        };
+
+        assert_eq!(outgoing_state.last_sent_message_id, Some(0));
+        assert_eq!(
+            outgoing_state.sent_messages.get(&0),
+            Some(&outgoing_proposal)
+        );
+    }
+
     #[test]
     fn handle_incoming_proposal_message_evicts_inactive_streams() {
         let mut state = State::new();
@@ -476,15 +571,17 @@ mod tests {
         let active_existing: HeightAndRound = (1, 3).into();
         let new_stream: HeightAndRound = (1, 4).into();
 
-        state
-            .active_streams
-            .insert(inactive_incoming, ActiveStream::new_incoming());
+        state.active_streams.insert(
+            inactive_incoming,
+            ActiveStream::new_incoming(PeerId::random()),
+        );
         state
             .active_streams
             .insert(inactive_outgoing, ActiveStream::new_outgoing());
-        state
-            .active_streams
-            .insert(active_existing, ActiveStream::new_incoming());
+        state.active_streams.insert(
+            active_existing,
+            ActiveStream::new_incoming(PeerId::random()),
+        );
 
         state
             .active_streams
@@ -504,7 +601,8 @@ mod tests {
             message: StreamMessageBody::Content(proposal),
         };
 
-        let events = handle_incoming_proposal_message(&mut state, message, PeerId::random());
+        let events =
+            handle_incoming_proposal_message(&mut state, message, PeerId::random()).unwrap();
 
         assert_eq!(events.len(), 1);
         assert!(!state.active_streams.contains_key(&inactive_incoming));
@@ -521,9 +619,10 @@ mod tests {
         let active_existing: HeightAndRound = (1, 3).into();
         let new_stream: HeightAndRound = (1, 4).into();
 
-        state
-            .active_streams
-            .insert(inactive_incoming, ActiveStream::new_incoming());
+        state.active_streams.insert(
+            inactive_incoming,
+            ActiveStream::new_incoming(PeerId::random()),
+        );
         state
             .active_streams
             .insert(inactive_outgoing, ActiveStream::new_outgoing());
```

### crates/p2p/src/consensus/behaviour.rs
```diff
@@ -166,14 +166,17 @@ impl ApplicationBehaviour for Behaviour {
                 message,
             } => match message.topic {
                 hash if hash == topic_proposals_hash => {
-                    if let Ok(stream_msg) = StreamMessage::from_protobuf_bytes(&message.data) {
-                        let events =
-                            handle_incoming_proposal_message(state, stream_msg, propagation_source);
+                    let Ok(stream_msg) = StreamMessage::from_protobuf_bytes(&message.data) else {
+                        error!("Failed to parse proposal message with id: {}", message_id);
+                        return;
+                    };
+
+                    if let Some(events) =
+                        handle_incoming_proposal_message(state, stream_msg, propagation_source)
+                    {
                         for event in events {
                             let _ = event_sender.send(event);
                         }
-                    } else {
-                        error!("Failed to parse proposal message with id: {}", message_id);
                     }
                 }
                 hash if hash == topic_votes_hash => {
```

### crates/p2p/src/consensus/stream.rs
```diff
@@ -78,8 +78,8 @@ pub enum StreamState<T> {
 
 impl<T> StreamState<T> {
     /// Create a new incoming stream state.
-    pub fn new_incoming() -> Self {
-        Self::Incoming(IncomingStreamState::new())
+    pub fn new_incoming(source: libp2p::PeerId) -> Self {
+        Self::Incoming(IncomingStreamState::new(source))
     }
 
     /// Create a new outgoing stream state.
@@ -91,6 +91,8 @@ impl<T> StreamState<T> {
 /// State of a stream that is receiving messages.
 #[derive(Debug)]
 pub struct IncomingStreamState<T> {
+    /// Source of the incoming stream messages.
+    pub source: libp2p::PeerId,
     /// The next message id that is expected.
     pub next_message_id: u64,
     /// The messages that have been received.
@@ -100,8 +102,9 @@ pub struct IncomingStreamState<T> {
 }
 
 impl<T> IncomingStreamState<T> {
-    fn new() -> Self {
+    fn new(source: libp2p::PeerId) -> Self {
         Self {
+            source,
             next_message_id: 0,
             received_messages: HashMap::new(),
             fin_message_id: None,
```
