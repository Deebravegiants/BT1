# [?] Summonerd: Correctly handle contribution handler crashes

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2023-10-21
Source: https://github.com/penumbra-zone/penumbra/commit/8e215d745409627071e93c0052c180efd667c9c3
Type: security-commit

## Details
Summonerd: Correctly handle contribution handler crashes

Now we correctly bubble these upstream and crash the entire server.

This is what we want, because these crashes are unexpected and
indicative of some actual issue.

## Patch
### tools/summonerd/src/coordinator.rs
```diff
@@ -1,6 +1,7 @@
 use std::{cmp, collections::HashMap, time::Duration};
 
 use anyhow::{anyhow, Result};
+use futures::FutureExt;
 use penumbra_keys::Address;
 use penumbra_num::Amount;
 use tokio::sync::mpsc::{self};
@@ -199,16 +200,22 @@ impl Coordinator {
         enum Event {
             NewParticipant(Participant, Amount),
             ContributionDone,
+            ContributionHandlerFinished(Result<()>),
         }
 
         let (contribution_handler, start_contribution_tx, done_contribution_rx) =
             ContributionHandler::new(self.storage);
-        tokio::spawn(contribution_handler.run::<P>());
+        let wait_for_contribution_handler = tokio::spawn(contribution_handler.run::<P>());
         // Merge the events from both being notified of new participants, and of completed
         // contributions.
         let mut stream = ReceiverStream::new(self.new_participant_rx)
             .map(|(participant, bid)| Event::NewParticipant(participant, bid))
-            .merge(ReceiverStream::new(done_contribution_rx).map(|_| Event::ContributionDone));
+            .merge(ReceiverStream::new(done_contribution_rx).map(|_| Event::ContributionDone))
+            .merge(wait_for_contribution_handler.into_stream().map(|x| {
+                Event::ContributionHandlerFinished(x.unwrap_or(Err(anyhow!(
+                    "failed to join on contribution handler handle"
+                ))))
+            }));
 
         // We start by needing a contribution.
         let mut want_contribution = true;
@@ -230,6 +237,11 @@ impl Coordinator {
                     want_contribution = true;
                     None
                 }
+                Some(Event::ContributionHandlerFinished(why)) => {
+                    return Err(why
+                        .err()
+                        .unwrap_or(anyhow!("contribution handler finished with no reason")));
+                }
             };
             // 2. Score connections
             self.participants.prune();
```
