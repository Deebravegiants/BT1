# [?] merge: GHSA-jhpp-8h75-7pv5 into combined-security-fixes-ci

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2026-09-17
Source: https://github.com/ZcashFoundation/zebra/commit/f173418dd2d01f7524d026853fb68c7e51e4c467
Type: security-commit

## Details
merge: GHSA-jhpp-8h75-7pv5 into combined-security-fixes-ci

## Patch
### .changes/unreleased/zebra-network-Changed-20260902-100001.yaml
```diff
@@ -0,0 +1,8 @@
+project: zebra-network
+kind: Changed
+body: 'Peer bans now expire after 24 hours, matching `zcashd`''s
+  `DEFAULT_MISBEHAVING_BANTIME`. Bans were previously kept until restart. A peer
+  whose ban has lapsed is banned again as soon as it misbehaves again. Lapsed
+  bans are pruned when a new ban is applied
+  ([#11255](https://github.com/ZcashFoundation/zebra/issues/11255)).'
+time: 2026-09-02T10:00:01.000000000Z
```

### .changes/unreleased/zebra-network-Security-20260901-120000.yaml
```diff
@@ -0,0 +1,8 @@
+project: zebra-network
+kind: Security
+body: 'Peer misbehavior bans now apply to the whole peer group — one IPv4 address,
+  or one IPv6 `/64` subnet — instead of a single address. Bans were previously
+  keyed by the full address, so a peer could avoid its ban by reconnecting from
+  another of the 2^64 addresses in its `/64`
+  ([#11255](https://github.com/ZcashFoundation/zebra/issues/11255)).'
+time: 2026-09-01T12:00:00.000000000Z
```

### .changes/unreleased/zebra-network-breaking-20260901-120002.yaml
```diff
@@ -0,0 +1,13 @@
+project: zebra-network
+kind: breaking
+body: 'Removed the `misbehavior_score` field and `MetaAddr::misbehavior` method.
+  Misbehavior is now tracked per peer group by the `AddressBook`, and read with
+  the new `AddressBook::misbehavior_score` method, also available on the
+  `AddressBookPeers` trait: currently it returns `MAX_PEER_MISBEHAVIOR_SCORE`
+  for a banned group and `0` otherwise, because scores are not currently
+  accumulated since those are the only two scores being used.
+  `AddressBook::bans` now returns the new `BanList` type instead of an
+  `Arc<IndexMap<IpAddr, Instant>>`; query it with `BanList::is_banned`, which
+  applies both the peer group mapping and ban expiry
+  ([#11255](https://github.com/ZcashFoundation/zebra/issues/11255)).'
+time: 2026-09-01T12:00:02.000000000Z
```

### .changes/unreleased/zebra-rpc-breaking-20260901-120003.yaml
```diff
@@ -0,0 +1,8 @@
+project: zebra-rpc
+kind: breaking
+body: 'Replaced `impl From<MetaAddr> for PeerInfo` with
+  `PeerInfo::from_meta_addr(meta_addr, banscore)`. The `banscore` field of
+  `getpeerinfo` now comes from the address book''s per-peer-group ban state, so
+  every address in an IPv6 `/64` reports the same score
+  ([#11255](https://github.com/ZcashFoundation/zebra/issues/11255)).'
+time: 2026-09-01T12:00:03.000000000Z
```

### .changes/unreleased/zebrad-Changed-20260902-100002.yaml
```diff
@@ -0,0 +1,7 @@
+project: zebrad
+kind: Changed
+body: 'Peer bans now expire after 24 hours instead of lasting until Zebra
+  restarts, so a peer banned by mistake — or one sharing an IPv6 `/64` with a
+  misbehaving peer — is not shut out permanently
+  ([#11255](https://github.com/ZcashFoundation/zebra/issues/11255)).'
+time: 2026-09-02T10:00:02.000000000Z
```

### .changes/unreleased/zebrad-Security-20260901-120001.yaml
```diff
@@ -0,0 +1,7 @@
+project: zebrad
+kind: Security
+body: 'Misbehaving peers can no longer avoid being banned by reconnecting from a
+  different address in the same IPv6 `/64` allocation: bans now apply to the
+  whole peer group
+  ([#11255](https://github.com/ZcashFoundation/zebra/issues/11255)).'
+time: 2026-09-01T12:00:01.000000000Z
```

### zebra-network/src/address_book.rs
```diff
@@ -21,7 +21,7 @@ use crate::{
     meta_addr::MetaAddrChange,
     protocol::external::{canonical_peer_addr, canonical_socket_addr, connection_limit_key},
     types::MetaAddr,
-    AddressBookPeers, PeerAddrState, PeerSocketAddr,
+    AddressBookPeers, BanList, PeerAddrState, PeerSocketAddr,
 };
 
 #[cfg(test)]
@@ -76,8 +76,13 @@ pub struct AddressBook {
     // TODO: Replace with `by_ip: HashMap<IpAddr, BTreeMap<DateTime32, MetaAddr>>` to support configured `max_connections_per_ip` greater than 1
     most_recent_by_ip: Option<HashMap<IpAddr, MetaAddr>>,
 
-    /// A list of banned addresses, with the time they were banned.
-    bans_by_ip: Arc<IndexMap<IpAddr, Instant>>,
+    /// The peer groups banned for misbehaviour.
+    ///
+    /// [`BanList`] applies the peer group mapping and ban expiry, so banning an
+    /// IPv6 peer bans its whole `/64`: otherwise a peer holding a `/64` evades
+    /// its ban by reconnecting from any of the 2⁶⁴ other addresses it already
+    /// controls.
+    bans: BanList,
 
     /// The local listener address.
     local_listener: SocketAddr,
@@ -161,7 +166,7 @@ impl AddressBook {
             address_metrics_tx,
             last_address_log: None,
             most_recent_by_ip: should_limit_outbound_conns_per_ip.then(HashMap::new),
-            bans_by_ip: Default::default(),
+            bans: Default::default(),
         };
 
         new_book.update_metrics(instant_now, chrono_now);
@@ -433,7 +438,7 @@ impl AddressBook {
     /// mutex, so refreshing per change makes a batch quadratic.
     #[allow(clippy::unwrap_in_result)]
     fn update_without_metrics(&mut self, change: MetaAddrChange) -> Option<MetaAddr> {
-        if self.bans_by_ip.contains_key(&change.addr().ip()) {
+        if self.bans.is_banned(change.addr().ip()) {
             // Remote peers control how often this fires, so keep it below `warn` (#11134).
             tracing::debug!(
                 ?change,
@@ -462,29 +467,48 @@ impl AddressBook {
         );
 
         if let Some(ref updated) = updated {
-            if updated.misbehavior() >= constants::MAX_PEER_MISBEHAVIOR_SCORE {
-                // Ban and skip outbound connections with excessively misbehaving peers.
-                let banned_ip = updated.addr.ip();
-                let bans_by_ip = Arc::make_mut(&mut self.bans_by_ip);
-
-                bans_by_ip.insert(banned_ip, Instant::now());
-                if bans_by_ip.len() > constants::MAX_BANNED_IPS {
-                    // Remove the oldest banned IP from the address book.
-                    bans_by_ip.shift_remove_index(0);
-                }
+            let score = change.misbehavior_score();
+            // Currently, scores are always either `0` or
+            // `MAX_PEER_MISBEHAVIOR_SCORE` (ban), so there is no need to
+            // accumulate scores. Do that here if we ever support partial
+            // scores.
+
+            if score != 0 && score != constants::MAX_PEER_MISBEHAVIOR_SCORE {
+                warn!(
+                    ?change,
+                    score,
+                    expected = constants::MAX_PEER_MISBEHAVIOR_SCORE,
+                    "programming error: misbehavior score is not 0 or \
+                     MAX_PEER_MISBEHAVIOR_SCORE, scores are not accumulated, \
+                     so a score below the threshold is dropped",
+                );
+            }
+
+            if score >= constants::MAX_PEER_MISBEHAVIOR_SCORE {
+                // # Security
+                //
+                // Ban the peer's whole group, not the individual address. A peer
+                // that rotates through the addresses of its `/64` — or just
+                // reconnects from a new source port, which is a different
+                // address book entry — would otherwise evade the ban.
+                let group = connection_limit_key(updated.addr.ip());
+                self.bans.ban(group);
 
                 // `most_recent_by_ip` is only populated when
                 // `max_connections_per_ip == 1`. The ban path runs for any
                 // configured value, so we must guard the optional cache rather
                 // than unwrap it.
                 if let Some(most_recent_by_ip) = self.most_recent_by_ip.as_mut() {
-                    most_recent_by_ip.remove(&connection_limit_key(banned_ip));
+                    most_recent_by_ip.remove(&group);
                 }
 
+                // Remove every address in the banned group, not just the one
+                // that crossed the threshold: the rest of an IPv6 `/64` belongs
+                // to the same peer.
                 let banned_addrs: Vec<_> = self
                     .by_addr
                     .keys()
-                    .filter(|addr| addr.ip() == banned_ip)
+                    .filter(|addr| connection_limit_key(addr.ip()) == group)
                     .cloned()
                     .collect();
 
@@ -672,7 +696,7 @@ impl AddressBook {
         self.by_addr
             .values()
             .filter(move |peer| {
-                !self.bans_by_ip.contains_key(&peer.addr.ip())
+                !self.bans.is_banned(peer.addr.ip())
                     && peer.is_ready_for_connection_attempt(instant_now, chrono_now, &self.network)
                     && self.is_ready_for_connection_attempt_with_ip(&peer.addr.ip(), chrono_now)
             })
@@ -710,9 +734,25 @@ impl AddressBook {
             .cloned()
     }
 
-    /// Returns banned IP addresses.
-    pub fn bans(&self) -> Arc<IndexMap<IpAddr, Instant>> {
-        self.bans_by_ip.clone()
+    /// Returns a snapshot of the banned peer groups.
+    pub fn bans(&self) -> BanList {
+        self.bans.clone()
+    }
+
+    /// Returns the misbehavior score for the peer group containing `addr`:
+    /// [`MAX_PEER_MISBEHAVIOR_SCORE`](constants::MAX_PEER_MISBEHAVIOR_SCORE) if
+    /// the group is banned, and `0` otherwise.
+    ///
+    /// Scores are not accumulated, so a group is either banned or unscored.
+    /// Bans apply per peer group — one IPv4 address, or one IPv6 `/64` subnet
+    /// — so every address in a group reports the same score. See
+    /// [`connection_limit_key`].
+    pub fn misbehavior_score(&self, addr: PeerSocketAddr) -> u32 {
+        if self.bans.is_banned(addr.ip()) {
+            constants::MAX_PEER_MISBEHAVIOR_SCORE
+        } else {
+            0
+        }
     }
 
     /// Returns the number of entries in this address book.
@@ -857,6 +897,10 @@ impl AddressBookPeers for AddressBook {
         }
         self.update(MetaAddr::new_initial_peer(peer)).is_some()
     }
+
+    fn misbehavior_score(&self, addr: PeerSocketAddr) -> u32 {
+        AddressBook::misbehavior_score(self, addr)
+    }
 }
 
 impl AddressBookPeers for Arc<Mutex<AddressBook>> {
@@ -871,6 +915,12 @@ impl AddressBookPeers for Arc<Mutex<AddressBook>> {
             .expect("panic in a previous thread that was holding the mutex")
             .add_peer(peer)
     }
+
+    fn misbehavior_score(&self, addr: PeerSocketAddr) -> u32 {
+        self.lock()
+            .expect("panic in a previous thread that was holding the mutex")
+            .misbehavior_score(addr)
+    }
 }
 
 impl Extend<MetaAddrChange> for AddressBook {
@@ -911,7 +961,7 @@ impl Clone for AddressBook {
             address_metrics_tx,
             last_address_log: None,
             most_recent_by_ip: self.most_recent_by_ip.clone(),
-            bans_by_ip: self.bans_by_ip.clone(),
+            bans: self.bans.clone(),
         }
     }
 }
```

### zebra-network/src/address_book/tests/vectors.rs
```diff
@@ -1,6 +1,9 @@
 //! Fixed test vectors for the address book.
 
-use std::time::Instant;
+use std::{
+    net::IpAddr,
+    time::{Duration, Instant},
+};
 
 use chrono::Utc;
 use tracing::Span;
@@ -11,7 +14,10 @@ use zebra_chain::{
 };
 
 use crate::{
-    constants::{DEFAULT_MAX_CONNS_PER_IP, MAX_ADDRS_IN_ADDRESS_BOOK, MAX_PEER_MISBEHAVIOR_SCORE},
+    constants::{
+        BAN_DURATION, DEFAULT_MAX_CONNS_PER_IP, MAX_ADDRS_IN_ADDRESS_BOOK,
+        MAX_PEER_MISBEHAVIOR_SCORE,
+    },
     meta_addr::{MetaAddr, MetaAddrChange},
     protocol::external::types::PeerServices,
     AddressBook,
@@ -105,7 +111,7 @@ fn misbehavior_ban_does_not_panic_with_max_connections_per_ip_above_one() {
     });
 
     assert!(
-        address_book.bans().contains_key(&banned_addr.ip()),
+        address_book.bans().is_banned(banned_addr.ip()),
         "ban-threshold misbehavior should ban the peer IP"
     );
     assert!(
@@ -459,7 +465,7 @@ fn ban_removes_every_entry_for_the_banned_ip() {
     });
 
     assert!(
-        address_book.bans().contains_key(&banned_addr.ip()),
+        address_book.bans().is_banned(banned_addr.ip()),
         "ban-threshold misbehavior should ban the peer IP",
     );
     assert_eq!(
@@ -480,3 +486,347 @@ fn ban_removes_every_entry_for_the_banned_ip() {
         "a banned IP must never be a reconnection candidate",
     );
 }
+
+/// A peer that rotates through the addresses of one IPv6 `/64` must not evade
+/// a misbehavior ban.
+///
+/// Bans used to be keyed by the full address, so a peer with a `/64` could
+/// misbehave from each of its 2^64 addresses in turn and never be shut out.
+#[test]
+fn ipv6_rotation_within_one_64_cannot_evade_a_ban() {
+    let mut address_book = AddressBook::new(
+        "0.0.0.0:0".parse().unwrap(),
+        &Mainnet,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::current(),
+    );
+
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: "[2001:db8::1]:8233".parse().unwrap(),
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+
+    let group: IpAddr = "2001:db8::".parse().unwrap();
+    assert!(
+        address_book.bans().is_banned(group),
+        "the ban should be keyed on the /64, not the individual address"
+    );
+
+    // Every address in the banned /64 is now rejected, including ones that
+    // never misbehaved themselves.
+    let untouched: crate::PeerSocketAddr = "[2001:db8::dead:beef]:8233".parse().unwrap();
+    address_book.update(gossiped_change(
+        untouched,
+        PeerServices::NODE_NETWORK,
+        DateTime32::MIN,
+    ));
+    assert!(
+        address_book.get(untouched).is_none(),
+        "a fresh address in the banned /64 must not be added to the address book"
+    );
+
+    // A different /64 is unaffected.
+    let other: crate::PeerSocketAddr = "[2001:db8:1::1]:8233".parse().unwrap();
+    address_book.update(gossiped_change(
+        other,
+        PeerServices::NODE_NETWORK,
+        DateTime32::MIN,
+    ));
+    assert!(
+        address_book.get(other).is_some(),
+        "an address in a different /64 should still be accepted"
+    );
+}
+
+/// IPv4 peers are grouped per address, so one misbehaving IPv4 peer must not
+/// ban its neighbours.
+#[test]
+fn ipv4_ban_does_not_affect_neighbouring_addresses() {
+    let mut address_book = AddressBook::new(
+        "0.0.0.0:0".parse().unwrap(),
+        &Mainnet,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::current(),
+    );
+
+    let misbehaving: crate::PeerSocketAddr = "192.0.2.10:8233".parse().unwrap();
+    let neighbour: crate::PeerSocketAddr = "192.0.2.11:8233".parse().unwrap();
+
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: misbehaving,
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+
+    assert!(
+        address_book.bans().is_banned(misbehaving.ip()),
+        "the misbehaving IPv4 address should be banned"
+    );
+
+    address_book.update(gossiped_change(
+        neighbour,
+        PeerServices::NODE_NETWORK,
+        DateTime32::MIN,
+    ));
+    assert!(
+        address_book.get(neighbour).is_some(),
+        "a neighbouring IPv4 address in the same /24 must not be banned"
+    );
+}
+
+/// Scores are not currently accumulated: a score at
+/// `MAX_PEER_MISBEHAVIOR_SCORE` bans the peer group on its own, and a score
+/// below it is dropped.
+///
+/// Every score Zebra produces is `0` or `MAX_PEER_MISBEHAVIOR_SCORE`, so a
+/// score below the threshold is a programming error, which the address book
+/// logs. It is still checked against the threshold rather than against zero, so
+/// this path keeps working if intermediate scores and accumulation are ever
+/// added back.
+///
+/// Change this test if we ever support partial scores.
+#[test]
+fn only_a_threshold_misbehavior_score_bans_the_peer_group() {
+    for (score, should_ban) in [
+        (1, false),
+        (MAX_PEER_MISBEHAVIOR_SCORE - 1, false),
+        (MAX_PEER_MISBEHAVIOR_SCORE, true),
+        (MAX_PEER_MISBEHAVIOR_SCORE + 1, true),
+    ] {
+        let mut address_book = AddressBook::new(
+            "0.0.0.0:0".parse().unwrap(),
+            &Mainnet,
+            DEFAULT_MAX_CONNS_PER_IP,
+            Span::current(),
+        );
+
+        let misbehaving: crate::PeerSocketAddr = "[2001:db8::1]:8233".parse().unwrap();
+        address_book.update(MetaAddrChange::UpdateMisbehavior {
+            addr: misbehaving,
+            score_increment: score,
+        });
+
+        assert_eq!(
+            address_book.bans().is_banned(misbehaving.ip()),
+            should_ban,
+            "a misbehavior score of {score} should ban the peer group: {should_ban}"
+        );
+        assert_eq!(
+            address_book.misbehavior_score(misbehaving),
+            if should_ban {
+                MAX_PEER_MISBEHAVIOR_SCORE
+            } else {
+                0
+            },
+            "a score below the threshold is dropped, not stored: {score}"
+        );
+    }
+}
+
+/// The score reported for an address is its whole peer group's ban state, which
+/// is what `getpeerinfo` surfaces as `banscore`.
+#[test]
+fn misbehavior_score_is_reported_per_group() {
+    let mut address_book = AddressBook::new(
+        "0.0.0.0:0".parse().unwrap(),
+        &Mainnet,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::current(),
+    );
+
+    let banned: crate::PeerSocketAddr = "[2001:db8::1]:8233".parse().unwrap();
+    let sibling: crate::PeerSocketAddr = "[2001:db8::2]:8233".parse().unwrap();
+    let other_group: crate::PeerSocketAddr = "[2001:db8:1::1]:8233".parse().unwrap();
+
+    for addr in [banned, sibling, other_group] {
+        assert_eq!(
+            address_book.misbehavior_score(addr),
+            0,
+            "an unbanned group should report no score: {addr:?}"
+        );
+    }
+
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: banned,
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+
+    assert_eq!(
+        address_book.misbehavior_score(banned),
+        MAX_PEER_MISBEHAVIOR_SCORE,
+        "the banned address should report the ban score"
+    );
+    assert_eq!(
+        address_book.misbehavior_score(sibling),
+        MAX_PEER_MISBEHAVIOR_SCORE,
+        "a sibling in the same /64 should report the same score"
+    );
+    assert_eq!(
+        address_book.misbehavior_score(other_group),
+        0,
+        "an address in a different /64 should report no score"
+    );
+}
+
+/// A ban is enforced right up to `BAN_DURATION`, lapses at exactly
+/// `BAN_DURATION`, and the peer group is accepted again once it has.
+#[tokio::test(start_paused = true)]
+async fn bans_expire_after_the_ban_duration() {
+    let mut address_book = AddressBook::new(
+        "0.0.0.0:0".parse().unwrap(),
+        &Mainnet,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::current(),
+    );
+
+    let banned: crate::PeerSocketAddr = "[2001:db8::1]:8233".parse().unwrap();
+
+    // A fresh ban is enforced.
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: banned,
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+    assert!(
+        address_book.bans().is_banned(banned.ip()),
+        "a fresh ban should be enforced"
+    );
+    address_book.update(gossiped_change(
+        banned,
+        PeerServices::NODE_NETWORK,
+        DateTime32::MIN,
+    ));
+    assert!(
+        address_book.get(banned).is_none(),
+        "a banned peer should not be re-added to the address book"
+    );
+
+    // The ban is still enforced just before it lapses.
+    tokio::time::advance(BAN_DURATION - Duration::from_nanos(1)).await;
+    assert!(
+        address_book.bans().is_banned(banned.ip()),
+        "a ban should be enforced right up to BAN_DURATION"
+    );
+
+    // Then it lapses.
+    tokio::time::advance(Duration::from_nanos(1)).await;
+    assert!(
+        !address_book.bans().is_banned(banned.ip()),
+        "a ban should lapse at exactly BAN_DURATION"
+    );
+    assert_eq!(
+        address_book.misbehavior_score(banned),
+        0,
+        "a lapsed ban should no longer be reported as a score"
+    );
+
+    // The peer can be learned about again once its ban lapses.
+    let now: DateTime32 = Utc::now().try_into().expect("will succeed until 2038");
+    address_book.update(gossiped_change(banned, PeerServices::NODE_NETWORK, now));
+    assert!(
+        address_book.get(banned).is_some(),
+        "a peer whose ban has lapsed should be accepted again"
+    );
+}
+
+/// Applying a new ban prunes lapsed bans, so they don't occupy the
+/// `MAX_BANNED_IPS` slots that active bans need.
+#[tokio::test(start_paused = true)]
+async fn applying_a_ban_prunes_lapsed_bans() {
+    let mut address_book = AddressBook::new(
+        "0.0.0.0:0".parse().unwrap(),
+        &Mainnet,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::current(),
+    );
+
+    let lapsed: crate::PeerSocketAddr = "[2001:db8:1::1]:8233".parse().unwrap();
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: lapsed,
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+
+    tokio::time::advance(BAN_DURATION).await;
+    assert!(
+        !address_book.bans().is_banned(lapsed.ip()),
+        "the ban should have lapsed"
+    );
+    assert_eq!(
+        address_book.bans().len(),
+        1,
+        "the lapsed entry is still present until pruned"
+    );
+
+    // Banning another group prunes the lapsed entry.
+    let fresh: crate::PeerSocketAddr = "[2001:db8:2::1]:8233".parse().unwrap();
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: fresh,
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+
+    let bans = address_book.bans();
+    assert!(
+        !bans.is_banned("2001:db8:1::".parse::<IpAddr>().unwrap()),
+        "the lapsed ban should have been pruned"
+    );
+    assert!(
+        bans.is_banned("2001:db8:2::".parse::<IpAddr>().unwrap()),
+        "the new ban should be present"
+    );
+    assert_eq!(bans.len(), 1, "only the new ban should remain");
+}
+
+/// Once a group's ban lapses, misbehaving again bans the whole group for a full
+/// `BAN_DURATION`: the lapsed entry neither blocks nor shortens the new ban.
+///
+/// Changes from a banned group are rejected, so this is the only way a group
+/// can be banned twice through the address book.
+#[tokio::test(start_paused = true)]
+async fn a_lapsed_group_can_be_banned_again() {
+    let mut address_book = AddressBook::new(
+        "0.0.0.0:0".parse().unwrap(),
+        &Mainnet,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::current(),
+    );
+
+    let banned: crate::PeerSocketAddr = "[2001:db8::1]:8233".parse().unwrap();
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: banned,
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+    assert!(address_book.bans().is_banned(banned.ip()));
+
+    tokio::time::advance(BAN_DURATION).await;
+    assert!(
+        !address_book.bans().is_banned(banned.ip()),
+        "the first ban should have lapsed"
+    );
+
+    // The group misbehaves again from a different address in the same /64.
+    let sibling: crate::PeerSocketAddr = "[2001:db8::2]:8233".parse().unwrap();
+    address_book.update(MetaAddrChange::UpdateMisbehavior {
+        addr: sibling,
+        score_increment: MAX_PEER_MISBEHAVIOR_SCORE,
+    });
+
+    assert_eq!(
+        address_book.bans().len(),
+        1,
+        "the sibling address must share the banned group's entry"
+    );
+    assert!(
+        address_book.bans().is_banned(banned.ip()),
+        "the new ban should cover the whole group"
+    );
+
+    // The new ban runs for a full BAN_DURATION from the re-ban.
+    tokio::time::advance(BAN_DURATION - Duration::from_nanos(1)).await;
+    assert!(
+        address_book.bans().is_banned(banned.ip()),
+        "the new ban should be enforced right up to its own deadline"
+    );
+    tokio::time::advance(Duration::from_nanos(1)).await;
+    assert!(
+        !address_book.bans().is_banned(banned.ip()),
+        "the new ban should lapse BAN_DURATION after the re-ban"
+    );
+}
```

### zebra-network/src/address_book_peers.rs
```diff
@@ -17,4 +17,16 @@ pub trait AddressBookPeers {
 
     /// Add a peer to the address book.
     fn add_peer(&mut self, peer: PeerSocketAddr) -> bool;
+
+    /// Returns the misbehavior score for the peer group containing `addr`:
+    /// [`MAX_PEER_MISBEHAVIOR_SCORE`](crate::constants::MAX_PEER_MISBEHAVIOR_SCORE)
+    /// if the group is banned, and `0` otherwise.
+    ///
+    /// Bans apply per peer group — one IPv4 address, or one IPv6 `/64` subnet —
+    /// so every address in a group reports the same score.
+    ///
+    /// Defaults to `0` for implementors that don't track misbehavior.
+    fn misbehavior_score(&self, _addr: PeerSocketAddr) -> u32 {
+        0
+    }
 }
```

### zebra-network/src/address_book_updater.rs
```diff
@@ -3,15 +3,14 @@
 
 use std::{
     cmp::max,
-    net::{IpAddr, SocketAddr},
+    net::SocketAddr,
     sync::Arc,
     task::{Context, Poll},
     time::Instant,
 };
 
 use chrono::Utc;
 use futures::future;
-use indexmap::IndexMap;
 use thiserror::Error;
 use tokio::{
     sync::{mpsc, oneshot, watch},
@@ -24,7 +23,7 @@ use crate::{
     address_book::AddressMetrics,
     address_book_peers::AddressBookPeers,
     meta_addr::{MetaAddr, MetaAddrChange},
-    AddressBook, BoxError, Config,
+    AddressBook, BanList, BoxError, Config,
 };
 
 #[cfg(test)]
@@ -172,7 +171,7 @@ struct AddressBookHandler {
     address_book: Arc<std::sync::Mutex<AddressBook>>,
 
     /// The channel used to publish the ban list when it changes.
-    bans_sender: Arc<watch::Sender<Arc<IndexMap<IpAddr, Instant>>>>,
+    bans_sender: Arc<watch::Sender<BanList>>,
 }
 
 impl AddressBookHandler {
@@ -202,10 +201,11 @@ impl AddressBookHandler {
 
                 // `UpdateMisbehavior` events should only be passed to `update()` here,
                 // so that this channel is always updated when new addresses are banned.
+                //
                 let bans = updated
                     .is_none()
                     .then(|| address_book.bans())
-                    .filter(|bans| bans.contains_key(&event_ip));
+                    .filter(|bans| bans.is_banned(event_ip));
 
                 // Don't hold the lock while sending the list of `bans`
                 drop(address_book);
@@ -296,7 +296,7 @@ impl AddressBookUpdater {
         local_listener: SocketAddr,
     ) -> (
         Arc<std::sync::Mutex<AddressBook>>,
-        watch::Receiver<Arc<IndexMap<IpAddr, Instant>>>,
+        watch::Receiver<BanList>,
         AddressBookChangeSender,
         AddressBookService,
         watch::Receiver<AddressMetrics>,
@@ -325,7 +325,7 @@ impl AddressBookUpdater {
         channel_size: usize,
     ) -> (
         Arc<std::sync::Mutex<AddressBook>>,
-        watch::Receiver<Arc<IndexMap<IpAddr, Instant>>>,
+        watch::Receiver<BanList>,
         AddressBookChangeSender,
         AddressBookService,
         watch::Receiver<AddressMetrics>,
```

### zebra-network/src/address_book_updater/tests.rs
```diff
@@ -12,7 +12,7 @@ use crate::{
     address_book_updater::{
         AddressBookRequest, AddressBookResponse, AddressBookUpdater, MIN_CHANNEL_SIZE,
     },
-    constants::DEFAULT_MAX_CONNS_PER_IP,
+    constants::{DEFAULT_MAX_CONNS_PER_IP, MAX_PEER_MISBEHAVIOR_SCORE},
     protocol::types::PeerServices,
     types::MetaAddr,
     AddressBook,
@@ -202,3 +202,48 @@ async fn concurrent_next_reconnect_peer_requests_return_distinct_peers() {
         "concurrent NextReconnectPeer requests must never return the same peer",
     );
 }
+
+/// Banning an IPv6 peer must publish the ban on the bans watch channel, so the
+/// peer set and inbound listener drop its connections.
+#[tokio::test]
+async fn banning_an_ipv6_group_publishes_the_ban() {
+    let _init_guard = zebra_test::init();
+
+    let address_book = AddressBook::new(
+        SocketAddr::from_str("0.0.0.0:0").unwrap(),
+        &Mainnet,
+        DEFAULT_MAX_CONNS_PER_IP,
+        Span::none(),
+    );
+
+    let (
+        _address_book,
+        bans_receiver,
+        _change_sender,
+        address_book_service,
+        _address_metrics,
+        _updater_guard,
+    ) = AddressBookUpdater::spawn_with_address_book(address_book, MIN_CHANNEL_SIZE);
+
+    let misbehaving: crate::PeerSocketAddr =
+        SocketAddr::from_str("[2001:db8::5]:8233").unwrap().into();
+
+    let response = address_book_service
+        .clone()
+        .oneshot(AddressBookRequest::Change(MetaAddr::new_misbehavior(
+            misbehaving,
+            MAX_PEER_MISBEHAVIOR_SCORE,
+        )))
+        .await
+        .expect("service should be running");
+    assert!(
+        matches!(response, AddressBookResponse::Updated(None)),
+        "a ban-threshold misbehavior change is not applied to the address book"
+    );
+
+    let bans = bans_receiver.borrow().clone();
+    assert!(
+        bans.is_banned("2001:db8::".parse::<std::net::IpAddr>().unwrap()),
+        "the ban must be published on the bans channel, keyed by peer group"
+    );
+}
```

### zebra-network/src/ban_list.rs
```diff
@@ -0,0 +1,92 @@
+//! The set of banned peer groups.
+
+use std::{collections::HashMap, net::IpAddr, sync::Arc};
+
+use tokio::time::Instant;
+
+use crate::{constants, protocol::external::connection_limit_key};
+
+#[cfg(test)]
+mod tests;
+
+/// The peer groups Zebra has banned for misbehaviour, and when each was banned.
+///
+/// Entries are keyed by peer group — one IPv4 address, or one IPv6 `/64` subnet
+/// — so a peer cannot dodge its ban by reconnecting from another address it
+/// already controls. Bans lapse after
+/// [`BAN_DURATION`](constants::BAN_DURATION).
+///
+/// # Security
+///
+/// This type owns both of those rules. It deliberately does not expose the
+/// underlying map: a caller doing its own lookup would have to remember to map
+/// the address to its peer group *and* to check the ban's age, and getting
+/// either wrong silently stops bans being enforced. Query it with
+/// [`BanList::is_banned`].
+///
+/// # Correctness
+///
+/// Cloning is cheap, and a clone is a snapshot: the map is shared behind an
+/// [`Arc`] and copied only when a ban is added. Snapshots stay correct as bans
+/// lapse, because [`BanList::is_banned`] checks each entry's age when it is
+/// queried, so holders don't need to be sent a new snapshot.
+#[derive(Clone, Debug, Default, PartialEq, Eq)]
+pub struct BanList {
+    /// The time each banned peer group was banned.
+    banned_at: Arc<HashMap<IpAddr, Instant>>,
+}
+
+impl BanList {
+    /// Returns `true` if `ip`'s peer group is banned, and the ban has not
+    /// lapsed.
+    pub fn is_banned(&self, ip: IpAddr) -> bool {
+        self.banned_at
+            .get(&connection_limit_key(ip))
+            .is_some_and(|banned_at| !Self::has_lapsed(*banned_at, Instant::now()))
+    }
+
+    /// Bans `ip`'s peer group, starting now.
+    ///
+    /// Re-banning an already-banned group extends its ban for another full
+    /// [`BAN_DURATION`](constants::BAN_DURATION).
+    pub(crate) fn ban(&mut self, ip: IpAddr) {
+        let now = Instant::now();
+        let banned_at = Arc::make_mut(&mut self.banned_at);
+
+        // Drop lapsed bans, so they don't occupy the slots that active bans
+        // need, and so snapshots stay small.
+        banned_at.retain(|_group, entry| !Self::has_lapsed(*entry, now));
+
+        // Inserting an already-banned group overwrites its ban time, which is
+        // exactly the refresh we want.
+        banned_at.insert(connection_limit_key(ip), now);
+
+        while banned_at.len() > constants::MAX_BANNED_IPS {
+            let oldest = banned_at
+                .iter()
+                .min_by_key(|(_group, entry)| **entry)
+                .map(|(group, _entry)| *group)
+                .expect("the map is over the limit, so it is not empty");
+            banned_at.remove(&oldest);
+        }
+    }
+
+    /// Returns `true` if a ban applied at `banned_at` has lapsed by `now`.
+    fn has_lapsed(banned_at: Instant, now: Instant) -> bool {
+        // Instants are monotonic, so `now` is normally at or after `banned_at`.
+        // Saturating to zero treats a clock oddity as "just banned" rather than
+        // "lapsed", which fails closed.
+        now.saturating_duration_since(banned_at) >= constants::BAN_DURATION
+    }
+
+    /// Returns the number of banned peer groups, including any whose bans have
+    /// lapsed but have not been pruned yet.
+    pub fn len(&self) -> usize {
+        self.banned_at.len()
+    }
+
+    /// Returns `true` if no peer group is banned.
+    pub fn is_empty(&self) -> bool {
+        self.banned_at.is_empty()
+    }
+}
```
