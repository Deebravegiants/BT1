# [?] Patch nomination DOS vector (#505)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2021-06-21
Source: https://github.com/moonbeam-foundation/moonbeam/commit/1cde8ef9c3bb8b3832ce0beeb8fb679e1530586d
Type: security-commit

## Details
Patch nomination DOS vector (#505)

* init

* save code, needs tests

* fix

* new design compile

* fix

* fix

* ts types

* migration without storage version usage

* debug logging and test failing on purpose assert false

* clean test

* bump versions and fix types in types bundle

* try ts test

* Update pallets/parachain-staking/src/lib.rs

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

* Update pallets/parachain-staking/src/lib.rs

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

* Update pallets/parachain-staking/src/lib.rs

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

* Update pallets/parachain-staking/src/tests.rs

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

* Update pallets/parachain-staking/src/lib.rs

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

* impl some review suggestions

* panic if nomination exists in collator state but not nominator state

* rebump runtime versions because master versions changed

* fix merge conflict

* split unit test into four unit test for each rule that needed to be tested

* remove debug trait used for debugging

* depecated -> deprecated typo

* Update pallets/parachain-staking/src/lib.rs

Co-authored-by: Joshy Orndorff <JoshOrndorff@users.noreply.github.com>

## Patch
### Cargo.lock
```diff
@@ -6647,7 +6647,7 @@ dependencies = [
 
 [[package]]
 name = "parachain-staking"
-version = "1.0.2"
+version = "1.0.3"
 dependencies = [
  "frame-benchmarking",
  "frame-support",
```

### moonbeam-types-bundle/index.ts
```diff
@@ -536,6 +536,19 @@ export const moonbeamDefinitions = {
           total: "Balance",
           state: "CollatorStatus",
         },
+        Collator2: {
+          id: "AccountId",
+          bond: "Balance",
+          nominators: "Vec<AccountId>",
+          top_nominators: "Vec<Bond>",
+          bottom_nominators: "Vec<Bond>",
+          total_counted: "Balance",
+          total_backing: "Balance",
+          state: "CollatorStatus",
+        },
+        NominatorAdded: {
+          _enum: ["AddedToBottom", { AddedToTop: "Balance" }],
+        },
         CollatorSnapshot: {
           bond: "Balance",
           nominators: "Vec<Bond>",
```

### pallets/parachain-staking/Cargo.toml
```diff
@@ -1,6 +1,6 @@
 [package]
 name = "parachain-staking"
-version = "1.0.2"
+version = "1.0.3"
 authors = ["PureStake"]
 edition = "2018"
 description = "parachain staking pallet for collator selection and reward distribution"
```

### pallets/parachain-staking/src/lib.rs
```diff
@@ -143,7 +143,8 @@ pub mod pallet {
 	}
 
 	#[derive(Encode, Decode, RuntimeDebug)]
-	/// Global collator state with commission fee, bonded stake, and nominations
+	/// DEPRECATED: This is the old storage schema. It is retained for purposes of storage migration
+	/// and should be removed in the future.
 	pub struct Collator<AccountId, Balance> {
 		pub id: AccountId,
 		pub bond: Balance,
@@ -152,18 +153,49 @@ pub mod pallet {
 		pub state: CollatorStatus,
 	}
 
+	#[derive(Encode, Decode, RuntimeDebug)]
+	/// Collator state with commission fee, bonded stake, and nominations
+	pub struct Collator2<AccountId, Balance> {
+		/// The account of this collator
+		pub id: AccountId,
+		/// This collator's self stake.
+		pub bond: Balance,
+		/// Set of all nominator AccountIds (to prevent >1 nomination per AccountId)
+		pub nominators: OrderedSet<AccountId>,
+		/// Top T::MaxNominatorsPerCollator::get() nominators, ordered greatest to least
+		pub top_nominators: Vec<Bond<AccountId, Balance>>,
+		/// Bottom nominators (unbounded), ordered least to greatest
+		pub bottom_nominators: Vec<Bond<AccountId, Balance>>,
+		/// Sum of top nominations + self.bond
+		pub total_counted: Balance,
+		/// Sum of all nominations + self.bond = (total_counted + uncounted)
+		pub total_backing: Balance,
+		/// Current status of the collator
+		pub state: CollatorStatus,
+	}
+
+	/// Convey relevant information describing if a nominator was added to the top or bottom
+	/// Nominations added to the top yield a new total
+	#[derive(Clone, Copy, PartialEq, Encode, Decode, RuntimeDebug)]
+	pub enum NominatorAdded<B> {
+		AddedToTop { new_total: B },
+		AddedToBottom,
+	}
+
 	impl<
 			A: Ord + Clone,
 			B: AtLeast32BitUnsigned + Ord + Copy + sp_std::ops::AddAssign + sp_std::ops::SubAssign,
-		> Collator<A, B>
+		> Collator2<A, B>
 	{
 		pub fn new(id: A, bond: B) -> Self {
-			let total = bond;
-			Collator {
+			Collator2 {
 				id,
 				bond,
 				nominators: OrderedSet::new(),
-				total,
+				top_nominators: Vec::new(),
+				bottom_nominators: Vec::new(),
+				total_counted: bond,
+				total_backing: bond,
 				state: CollatorStatus::default(), // default active
 			}
 		}
@@ -175,35 +207,226 @@ pub mod pallet {
 		}
 		pub fn bond_more(&mut self, more: B) {
 			self.bond += more;
-			self.total += more;
+			self.total_counted += more;
+			self.total_backing += more;
 		}
 		// Return None if less >= self.bond => collator must leave instead of bond less
 		pub fn bond_less(&mut self, less: B) -> Option<B> {
 			if self.bond > less {
 				self.bond -= less;
-				self.total -= less;
+				self.total_counted -= less;
+				self.total_backing -= less;
 				Some(self.bond)
 			} else {
 				None
 			}
 		}
-		pub fn inc_nominator(&mut self, nominator: A, more: B) {
-			for x in &mut self.nominators.0 {
+		/// Infallible sorted insertion
+		/// caller must verify !self.nominators.contains(nominator.owner) before call
+		pub fn add_top_nominator(&mut self, nominator: Bond<A, B>) {
+			match self
+				.top_nominators
+				.binary_search_by(|x| nominator.amount.cmp(&x.amount))
+			{
+				Ok(i) => self.top_nominators.insert(i, nominator),
+				Err(i) => self.top_nominators.insert(i, nominator),
+			}
+		}
+		/// Infallible sorted insertion
+		/// caller must verify !self.nominators.contains(nominator.owner) before call
+		pub fn add_bottom_nominator(&mut self, nominator: Bond<A, B>) {
+			match self
+				.bottom_nominators
+				.binary_search_by(|x| x.amount.cmp(&nominator.amount))
+			{
+				Ok(i) => self.bottom_nominators.insert(i, nominator),
+				Err(i) => self.bottom_nominators.insert(i, nominator),
+			}
+		}
+		/// Sort top nominators from greatest to least
+		pub fn sort_top_nominators(&mut self) {
+			self.top_nominators
+				.sort_unstable_by(|a, b| b.amount.cmp(&a.amount));
+		}
+		/// Sort bottom nominators from least to greatest
+		pub fn sort_bottom_nominators(&mut self) {
+			self.bottom_nominators
+				.sort_unstable_by(|a, b| a.amount.cmp(&b.amount));
+		}
+		/// Return Ok(Some(new_total)) if inserted into top
+		/// Return Ok(None) if inserted into bottom
+		/// Return Err if already exists in top or bottom
+		pub fn add_nominator<T: Config>(
+			&mut self,
+			acc: A,
+			amount: B,
+		) -> Result<NominatorAdded<B>, DispatchError> {
+			ensure!(
+				self.nominators.insert(acc.clone()),
+				Error::<T>::NominatorExists
+			);
+			self.total_backing += amount;
+			if (self.top_nominators.len() as u32) < T::MaxNominatorsPerCollator::get() {
+				self.add_top_nominator(Bond { owner: acc, amount });
+				self.total_counted += amount;
+				Ok(NominatorAdded::AddedToTop {
+					new_total: self.total_counted,
+				})
+			} else {
+				let last_nomination_in_top = self
+					.top_nominators
+					.pop()
+					.expect("self.top_nominators.len() >= T::Max exists >= 1 element in top");
+				if amount > last_nomination_in_top.amount {
+					// update total_counted with positive difference
+					self.total_counted += amount - last_nomination_in_top.amount;
+					// last nomination already popped from top_nominators
+					// insert new nominator into top_nominators
+					self.add_top_nominator(Bond { owner: acc, amount });
+					self.add_bottom_nominator(last_nomination_in_top);
+					Ok(NominatorAdded::AddedToTop {
+						new_total: self.total_counted,
+					})
+				} else {
+					// push previously popped last nomination into top_nominators
+					self.top_nominators.push(last_nomination_in_top);
+					self.add_bottom_nominator(Bond { owner: acc, amount });
+					Ok(NominatorAdded::AddedToBottom)
+				}
+			}
+		}
+		/// Return Ok((if_total_counted_changed, nominator's stake))
+		pub fn rm_nominator<T: Config>(
+			&mut self,
+			nominator: A,
+		) -> Result<(bool, B), DispatchError> {
+			ensure!(self.nominators.remove(&nominator), Error::<T>::NominatorDNE);
+			let mut nominator_stake: Option<B> = None;
+			self.top_nominators = self
+				.top_nominators
+				.clone()
+				.into_iter()
+				.filter_map(|nom| {
+					if nom.owner != nominator {
+						Some(nom)
+					} else {
+						nominator_stake = Some(nom.amount);
+						None
+					}
+				})
+				.collect();
+			if let Some(s) = nominator_stake {
+				// last element has largest amount as per ordering
+				if let Some(last) = self.bottom_nominators.pop() {
+					self.total_counted -= s - last.amount;
+					self.add_top_nominator(last);
+				} else {
+					self.total_counted -= s;
+				}
+				self.total_backing -= s;
+				return Ok((true, s));
+			}
+			self.bottom_nominators = self
+				.bottom_nominators
+				.clone()
+				.into_iter()
+				.filter_map(|nom| {
+					if nom.owner != nominator {
+						Some(nom)
+					} else {
+						nominator_stake = Some(nom.amount);
+						None
+					}
+				})
+				.collect();
+			let stake = nominator_stake.ok_or(Error::<T>::NominatorDNE)?;
+			self.total_backing -= stake;
+			Ok((false, stake))
+		}
+		/// Return true if in_top after call
+		/// Caller must verify before call that account is a nominator
+		pub fn inc_nominator(&mut self, nominator: A, more: B) -> bool {
+			let mut in_top = false;
+			for x in &mut self.top_nominators {
 				if x.owner == nominator {
 					x.amount += more;
-					self.total += more;
-					return;
+					self.total_counted += more;
+					self.total_backing += more;
+					in_top = true;
+					break;
+				}
+			}
+			if in_top {
+				self.sort_top_nominators();
+				return true;
+			}
+			let lowest_top = self
+				.top_nominators
+				.pop()
+				.expect("any bottom nominators => exists T::Max top nominators");
+			let mut move_2_top = false;
+			for x in &mut self.bottom_nominators {
+				if x.owner == nominator {
+					x.amount += more;
+					self.total_backing += more;
+					move_2_top = x.amount > lowest_top.amount;
+					break;
 				}
 			}
+			if move_2_top {
+				self.sort_bottom_nominators();
+				let highest_bottom = self.bottom_nominators.pop().expect("updated => exists");
+				self.total_counted += highest_bottom.amount - lowest_top.amount;
+				self.add_top_nominator(highest_bottom);
+				self.add_bottom_nominator(lowest_top);
+				true
+			} else {
+				// reset top_nominators from earlier pop
+				self.top_nominators.push(lowest_top);
+				self.sort_bottom_nominators();
+				false
+			}
 		}
-		pub fn dec_nominator(&mut self, nominator: A, less: B) {
-			for x in &mut self.nominators.0 {
+		/// Return true if in_top after call
+		pub fn dec_nominator(&mut self, nominator: A, less: B) -> bool {
+			let mut in_top = false;
+			let mut new_top: Option<Bond<A, B>> = None;
+			for x in &mut self.top_nominators {
+				if x.owner == nominator {
+					x.amount -= less;
+					self.total_counted -= less;
+					self.total_backing -= less;
+					if let Some(top_bottom) = self.bottom_nominators.pop() {
+						if top_bottom.amount > x.amount {
+							new_top = Some(top_bottom);
+						}
+					}
+					in_top = true;
+					break;
+				}
+			}
+			if in_top {
+				self.sort_top_nominators();
+				if let Some(new) = new_top {
+					let lowest_top = self.top_nominators.pop().expect("just updated => exists");
+					self.total_counted -= lowest_top.amount;
+					self.total_counted += new.amount;
+					self.add_top_nominator(new);
+					self.add_bottom_nominator(lowest_top);
+					return false;
+				} else {
+					return true;
+				}
+			}
+			for x in &mut self.bottom_nominators {
 				if x.owner == nominator {
 					x.amount -= less;
-					self.total -= less;
-					return;
+					self.total_backing -= less;
+					break;
 				}
 			}
+			self.sort_bottom_nominators();
+			false
 		}
 		pub fn go_offline(&mut self) {
 			self.state = CollatorStatus::Idle;
@@ -216,12 +439,37 @@ pub mod pallet {
 		}
 	}
 
-	impl<A: Clone, B: Copy> From<Collator<A, B>> for CollatorSnapshot<A, B> {
-		fn from(other: Collator<A, B>) -> CollatorSnapshot<A, B> {
+	impl<A: Clone + Ord, B: Ord + Copy> From<Collator<A, B>> for Collator2<A, B> {
+		fn from(other: Collator<A, B>) -> Collator2<A, B> {
+			// nominator set from Collator was bounded to max size of top_nominators
+			let mut top_nominators = other.nominators.0.clone();
+			// order greatest to least
+			top_nominators.sort_unstable_by(|a, b| b.amount.cmp(&a.amount));
+			Collator2 {
+				id: other.id,
+				bond: other.bond,
+				nominators: other
+					.nominators
+					.0
+					.iter()
+					.map(|Bond { owner, .. }| owner.clone())
+					.collect::<Vec<A>>()
+					.into(),
+				top_nominators,
+				bottom_nominators: Vec::new(),
+				total_counted: other.total,
+				total_backing: other.total,
+				state: other.state,
+			}
+		}
+	}
+
+	impl<A: Clone, B: Copy> From<Collator2<A, B>> for CollatorSnapshot<A, B> {
+		fn from(other: Collator2<A, B>) -> CollatorSnapshot<A, B> {
 			CollatorSnapshot {
 				bond: other.bond,
-				nominators: other.nominators.0,
-				total: other.total,
+				nominators: other.top_nominators,
+				total: other.total_counted,
 			}
 		}
 	}
@@ -404,7 +652,7 @@ pub mod pallet {
 		type BondDuration: Get<RoundIndex>;
 		/// Minimum number of selected candidates every round
 		type MinSelectedCandidates: Get<u32>;
-		/// Maximum nominators per collator
+		/// Maximum nominators counted per collator
 		type MaxNominatorsPerCollator: Get<u32>;
 		/// Maximum collators per nominator
 		type MaxCollatorsPerNominator: Get<u32>;
@@ -437,7 +685,6 @@ pub mod pallet {
 		AlreadyOffline,
 		AlreadyActive,
 		AlreadyLeaving,
-		TooManyNominators,
 		CannotActivateIfLeaving,
 		ExceedMaxCollatorsPerNom,
 		AlreadyNominatedCollator,
@@ -467,14 +714,19 @@ pub mod pallet {
 		CollatorScheduledExit(RoundIndex, T::AccountId, RoundIndex),
 		/// Account, Amount Unlocked, New Total Amt Locked
 		CollatorLeft(T::AccountId, BalanceOf<T>, BalanceOf<T>),
-		// Nominator, Collator, Old Nomination, New Nomination
-		NominationIncreased(T::AccountId, T::AccountId, BalanceOf<T>, BalanceOf<T>),
-		// Nominator, Collator, Old Nomination, New Nomination
-		NominationDecreased(T::AccountId, T::AccountId, BalanceOf<T>, BalanceOf<T>),
+		// Nominator, Collator, Old Nomination, Counted in Top, New Nomination
+		NominationIncreased(T::AccountId, T::AccountId, BalanceOf<T>, bool, BalanceOf<T>),
+		// Nominator, Collator, Old Nomination, Counted in Top, New Nomination
+		NominationDecreased(T::AccountId, T::AccountId, BalanceOf<T>, bool, BalanceOf<T>),
 		/// Nominator, Amount Unstaked
 		NominatorLeft(T::AccountId, BalanceOf<T>),
-		/// Nominator, Amount Locked, Collator, New Total Amt backing Collator
-		Nomination(T::AccountId, BalanceOf<T>, T::AccountId, BalanceOf<T>),
+		/// Nominator, Amount Locked, Collator, Nominator Position with New Total Backing if in Top
+		Nomination(
+			T::AccountId,
+			BalanceOf<T>,
+			T::AccountId,
+			NominatorAdded<BalanceOf<T>>,
+		),
 		/// Nominator, Collator, Amount Unstaked, New Total Amt Staked for Collator
 		NominatorLeftCollator(T::AccountId, T::AccountId, BalanceOf<T>, BalanceOf<T>),
 		/// Paid the account (nominator or collator) the balance as liquid rewards
@@ -507,13 +759,19 @@ pub mod pallet {
 
 	#[pallet::hooks]
 	impl<T: Config> Hooks<BlockNumberFor<T>> for Pallet<T> {
-		// This upgrade fixes a bug that may have led to an incorrect `Total` (total staked)
 		fn on_runtime_upgrade() -> Weight {
+			// migrate from Collator -> Collator2
+			for (acc, collator_state) in CollatorState::<T>::drain() {
+				let state: Collator2<T::AccountId, BalanceOf<T>> = collator_state.into();
+				<CollatorState2<T>>::insert(acc, state);
+			}
+
+			// correct any incorrectly set `Total`
 			let old_total = Total::<T>::get();
 			let mut new_total: BalanceOf<T> = 0u32.into();
 
-			for collator_state in CollatorState::<T>::iter_values() {
-				new_total += collator_state.total;
+			for collator_state in CollatorState2::<T>::iter_values() {
+				new_total += collator_state.total_backing;
 			}
 
 			Total::<T>::put(new_total);
@@ -587,7 +845,8 @@ pub mod pallet {
 
 	#[pallet::storage]
 	#[pallet::getter(fn collator_state)]
-	/// Get collator state associated with an account if account is collating else None
+	/// DEPRECATED: This is the old storage item. It is retained for purposes of storage migration
+	/// and should be removed in the future.
 	type CollatorState<T: Config> = StorageMap<
 		_,
 		Twox64Concat,
@@ -596,6 +855,17 @@ pub mod pallet {
 		OptionQuery,
 	>;
 
+	#[pallet::storage]
+	#[pallet::getter(fn collator_state2)]
+	/// Get collator state associated with an account if account is collating else None
+	type CollatorState2<T: Config> = StorageMap<
+		_,
+		Twox64Concat,
+		T::AccountId,
+		Collator2<T::AccountId, BalanceOf<T>>,
+		OptionQuery,
+	>;
+
 	#[pallet::storage]
 	#[pallet::getter(fn selected_candidates)]
 	/// The collator candidates selected for the current round
@@ -910,8 +1180,8 @@ pub mod pallet {
 				Error::<T>::CandidateExists
 			);
 			T::Currency::reserve(&acc, bond)?;
-			let candidate = Collator::new(acc.clone(), bond);
-			<CollatorState<T>>::insert(&acc, candidate);
+			let candidate = Collator2::new(acc.clone(), bond);
+			<CollatorState2<T>>::insert(&acc, candidate);
 			<CandidatePool<T>>::put(candidates);
 			let new_total = <Total<T>>::get().saturating_add(bond);
 			<Total<T>>::put(new_total);
@@ -924,7 +1194,7 @@ pub mod pallet {
 		#[pallet::weight(0)]
 		pub fn leave_candidates(origin: OriginFor<T>) -> DispatchResultWithPostInfo {
 			let collator = ensure_signed(origin)?;
-			let mut state = <CollatorState<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
+			let mut state = <CollatorState2<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
 			ensure!(!state.is_leaving(), Error::<T>::AlreadyLeaving);
 			let mut exits = <ExitQueue<T>>::get();
 			let now = <Round<T>>::get().current;
@@ -942,23 +1212,22 @@ pub mod pallet {
 				<CandidatePool<T>>::put(candidates);
 			}
 			<ExitQueue<T>>::put(exits);
-			<CollatorState<T>>::insert(&collator, state);
+			<CollatorState2<T>>::insert(&collator, state);
 			Self::deposit_event(Event::CollatorScheduledExit(now, collator, when));
 			Ok(().into())
 		}
 		/// Temporarily leave the set of collator candidates without unbonding
 		#[pallet::weight(0)]
 		pub fn go_offline(origin: OriginFor<T>) -> DispatchResultWithPostInfo {
 			let collator = ensure_signed(origin)?;
-			let mut state = <CollatorState<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
+			let mut state = <CollatorState2<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
 			ensure!(state.is_active(), Error::<T>::AlreadyOffline);
 			state.go_offline();
 			let mut candidates = <CandidatePool<T>>::get();
-			// TODO: investigate possible bug in this next line
 			if candidates.remove(&Bond::from_owner(collator.clone())) {
 				<CandidatePool<T>>::put(candidates);
 			}
-			<CollatorState<T>>::insert(&collator, state);
+			<CollatorState2<T>>::insert(&collator, state);
 			Self::deposit_event(Event::CollatorWentOffline(
 				<Round<T>>::get().current,
 				collator,
@@ -969,20 +1238,20 @@ pub mod pallet {
 		#[pallet::weight(0)]
 		pub fn go_online(origin: OriginFor<T>) -> DispatchResultWithPostInfo {
 			let collator = ensure_signed(origin)?;
-			let mut state = <CollatorState<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
+			let mut state = <CollatorState2<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
 			ensure!(!state.is_active(), Error::<T>::AlreadyActive);
 			ensure!(!state.is_leaving(), Error::<T>::CannotActivateIfLeaving);
 			state.go_online();
 			let mut candidates = <CandidatePool<T>>::get();
 			ensure!(
 				candidates.insert(Bond {
 					owner: collator.clone(),
-					amount: state.total
+					amount: state.total_counted
 				}),
 				Error::<T>::AlreadyActive
 			);
 			<CandidatePool<T>>::put(candidates);
-			<CollatorState<T>>::insert(&collator, state);
+			<CollatorState2<T>>::insert(&collator, state);
 			Self::deposit_event(Event::CollatorBackOnline(
 				<Round<T>>::get().current,
 				collator,
@@ -996,16 +1265,16 @@ pub mod pallet {
 			more: BalanceOf<T>,
 		) -> DispatchResultWithPostInfo {
 			let collator = ensure_signed(origin)?;
-			let mut state = <CollatorState<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
+			let mut state = <CollatorState2<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
 			ensure!(!state.is_leaving(), Error::<T>::CannotActivateIfLeaving);
 			T::Currency::reserve(&collator, more)?;
 			let before = state.bond;
 			state.bond_more(more);
 			let after = state.bond;
 			if state.is_active() {
-				Self::update_active(collator.clone(), state.total);
+				Self::update_active(collator.clone(), state.total_counted);
 			}
-			<CollatorState<T>>::insert(&collator, state);
+			<CollatorState2<T>>::insert(&collator, state);
 			let new_total = <Total<T>>::get().saturating_add(more);
 			<Total<T>>::put(new_total);
 			Self::deposit_event(Event::CollatorBondedMore(collator, before, after));
@@ -1018,7 +1287,7 @@ pub mod pallet {
 			less: BalanceOf<T>,
 		) -> DispatchResultWithPostInfo {
 			let collator = ensure_signed(origin)?;
-			let mut state = <CollatorState<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
+			let mut state = <CollatorState2<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
 			ensure!(!state.is_leaving(), Error::<T>::CannotActivateIfLeaving);
 			let before = state.bond;
 			let after = state
@@ -1030,9 +1299,9 @@ pub mod pallet {
 			);
 			T::Currency::unreserve(&collator, less);
 			if state.is_active() {
-				Self::update_active(collator.clone(), state.total);
+				Self::update_active(collator.clone(), state.total_counted);
 			}
-			<CollatorState<T>>::insert(&collator, state);
+			<CollatorState2<T>>::insert(&collator, state);
 			let new_total_staked = <Total<T>>::get().saturating_sub(less);
 			<Total<T>>::put(new_total_staked);
 			Self::deposit_event(Event::CollatorBondedLess(collator, before, after));
@@ -1074,29 +1343,19 @@ pub mod pallet {
 				ensure!(!Self::is_candidate(&acc), Error::<T>::CandidateExists);
 				Nominator::new(collator.clone(), amount)
 			};
-			let mut state = <CollatorState<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
-			ensure!(
-				(state.nominators.0.len() as u32) < T::MaxNominatorsPerCollator::get(),
-				Error::<T>::TooManyNominators
-			);
-			ensure!(
-				state.nominators.insert(Bond {
-					owner: acc.clone(),
-					amount,
-				}),
-				Error::<T>::NominatorExists
-			);
+			let mut state = <CollatorState2<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
+			let nominator_position = state.add_nominator::<T>(acc.clone(), amount)?;
 			T::Currency::reserve(&acc, amount)?;
-			let new_total = state.total + amount;
-			if state.is_active() {
-				Self::update_active(collator.clone(), new_total);
+			if let NominatorAdded::AddedToTop { new_total } = nominator_position {
+				if state.is_active() {
+					Self::update_active(collator.clone(), new_total);
+				}
 			}
 			let new_total_locked = <Total<T>>::get() + amount;
 			<Total<T>>::put(new_total_locked);
-			state.total = new_total;
-			<CollatorState<T>>::insert(&collator, state);
+			<CollatorState2<T>>::insert(&collator, state);
 			<NominatorState<T>>::insert(&acc, nominator);
-			Self::deposit_event(Event::Nomination(acc, amount, collator, new_total));
+			Self::deposit_event(Event::Nomination(acc, amount, collator, nominator_position));
 			Ok(().into())
 		}
 		/// Leave the set of nominators and, by implication, revoke all ongoing nominations
@@ -1130,24 +1389,24 @@ pub mod pallet {
 			let mut nominations =
 				<NominatorState<T>>::get(&nominator).ok_or(Error::<T>::NominatorDNE)?;
 			let mut collator =
-				<CollatorState<T>>::get(&candidate).ok_or(Error::<T>::CandidateDNE)?;
+				<CollatorState2<T>>::get(&candidate).ok_or(Error::<T>::CandidateDNE)?;
 			ensure!(
 				nominations.inc_nomination(candidate.clone(), more),
 				Error::<T>::NominationDNE
 			);
 			T::Currency::reserve(&nominator, more)?;
-			let before = collator.total;
-			collator.inc_nominator(nominator.clone(), more);
-			let after = collator.total;
-			if collator.is_active() {
-				Self::update_active(candidate.clone(), collator.total);
+			let before = collator.total_counted;
+			let in_top = collator.inc_nominator(nominator.clone(), more);
+			let after = collator.total_counted;
+			if collator.is_active() && (before != after) {
+				Self::update_active(candidate.clone(), after);
 			}
-			<CollatorState<T>>::insert(&candidate, collator);
+			<CollatorState2<T>>::insert(&candidate, collator);
 			<NominatorState<T>>::insert(&nominator, nominations);
 			let new_total_staked = <Total<T>>::get().saturating_add(more);
 			<Total<T>>::put(new_total_staked);
 			Self::deposit_event(Event::NominationIncreased(
-				nominator, candidate, before, after,
+				nominator, candidate, before, in_top, after,
 			));
 			Ok(().into())
 		}
@@ -1162,7 +1421,7 @@ pub mod pallet {
 			let mut nominations =
 				<NominatorState<T>>::get(&nominator).ok_or(Error::<T>::NominatorDNE)?;
 			let mut collator =
-				<CollatorState<T>>::get(&candidate).ok_or(Error::<T>::CandidateDNE)?;
+				<CollatorState2<T>>::get(&candidate).ok_or(Error::<T>::CandidateDNE)?;
 			let remaining = nominations
 				.dec_nomination(candidate.clone(), less)
 				.ok_or(Error::<T>::NominationDNE)?
@@ -1176,18 +1435,18 @@ pub mod pallet {
 				Error::<T>::NomBondBelowMin
 			);
 			T::Currency::unreserve(&nominator, less);
-			let before = collator.total;
-			collator.dec_nominator(nominator.clone(), less);
-			let after = collator.total;
-			if collator.is_active() {
-				Self::update_active(candidate.clone(), collator.total);
+			let before = collator.total_counted;
+			let in_top = collator.dec_nominator(nominator.clone(), less);
+			let after = collator.total_counted;
+			if collator.is_active() && (before != after) {
+				Self::update_active(candidate.clone(), after);
 			}
-			<CollatorState<T>>::insert(&candidate, collator);
+			<CollatorState2<T>>::insert(&candidate, collator);
 			<NominatorState<T>>::insert(&nominator, nominations);
 			let new_total_staked = <Total<T>>::get().saturating_sub(less);
 			<Total<T>>::put(new_total_staked);
 			Self::deposit_event(Event::NominationDecreased(
-				nominator, candidate, before, after,
+				nominator, candidate, before, in_top, after,
 			));
 			Ok(().into())
 		}
@@ -1198,7 +1457,7 @@ pub mod pallet {
 			<NominatorState<T>>::get(acc).is_some()
 		}
 		pub fn is_candidate(acc: &T::AccountId) -> bool {
-			<CollatorState<T>>::get(acc).is_some()
+			<CollatorState2<T>>::get(acc).is_some()
 		}
 		pub fn is_selected_candidate(acc: &T::AccountId) -> bool {
 			<SelectedCandidates<T>>::get().binary_search(acc).is_ok()
@@ -1255,33 +1514,16 @@ pub mod pallet {
 			nominator: T::AccountId,
 			collator: T::AccountId,
 		) -> DispatchResultWithPostInfo {
-			let mut state = <CollatorState<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
-			let mut exists: Option<BalanceOf<T>> = None;
-			let noms = state
-				.nominators
-				.0
-				.into_iter()
-				.filter_map(|nom| {
-					if nom.owner != nominator {
-						Some(nom)
-					} else {
-						exists = Some(nom.amount);
-						None
-					}
-				})
-				.collect();
-			let nominator_stake = exists.ok_or(Error::<T>::NominatorDNE)?;
-			let nominators = OrderedSet::from(noms);
+			let mut state = <CollatorState2<T>>::get(&collator).ok_or(Error::<T>::CandidateDNE)?;
+			let (total_changed, nominator_stake) = state.rm_nominator::<T>(nominator.clone())?;
 			T::Currency::unreserve(&nominator, nominator_stake);
-			state.nominators = nominators;
-			state.total -= nominator_stake;
-			if state.is_active() {
-				Self::update_active(collator.clone(), state.total);
+			if state.is_active() && total_changed {
+				Self::update_active(collator.clone(), state.total_counted);
 			}
 			let new_total_locked = <Total<T>>::get() - nominator_stake;
 			<Total<T>>::put(new_total_locked);
-			let new_total = state.total;
-			<CollatorState<T>>::insert(&collator, state);
+			let new_total = state.total_counted;
+			<CollatorState2<T>>::insert(&collator, state);
 			Self::deposit_event(Event::NominatorLeftCollator(
 				nominator,
 				collator,
@@ -1354,31 +1596,41 @@ pub mod pallet {
 					if x.amount > next {
 						Some(x)
 					} else {
-						if let Some(state) = <CollatorState<T>>::get(&x.owner) {
-							for bond in state.nominators.0 {
-								// return stake to nominator
+						if let Some(state) = <CollatorState2<T>>::get(&x.owner) {
+							// return stake to nominator
+							let return_stake = |bond: Bond<T::AccountId, BalanceOf<T>>| {
 								T::Currency::unreserve(&bond.owner, bond.amount);
 								// remove nomination from nominator state
-								if let Some(mut nominator) = <NominatorState<T>>::get(&bond.owner) {
-									if let Some(remaining) =
-										nominator.rm_nomination(x.owner.clone())
-									{
-										if remaining.is_zero() {
-											<NominatorState<T>>::remove(&bond.owner);
-										} else {
-											<NominatorState<T>>::insert(&bond.owner, nominator);
-										}
+								let mut nominator = NominatorState::<T>::get(&bond.owner).expect(
+									"Collator state and nominator state are consistent. 
+										Collator state has a record of this nomination. Therefore, 
+										Nominator state also has a record. qed.",
+								);
+								if let Some(remaining) = nominator.rm_nomination(x.owner.clone()) {
+									if remaining.is_zero() {
+										<NominatorState<T>>::remove(&bond.owner);
+									} else {
+										<NominatorState<T>>::insert(&bond.owner, nominator);
 									}
 								}
+							};
+							// return all top nominations
+							for bond in state.top_nominators {
+								return_stake(bond);
+							}
+							// return all bottom nominations
+							for bond in state.bottom_nominators {
+								return_stake(bond);
 							}
 							// return stake to collator
 							T::Currency::unreserve(&state.id, state.bond);
-							<CollatorState<T>>::remove(&x.owner);
-							let new_total_staked = <Total<T>>::get().saturating_sub(state.total);
+							<CollatorState2<T>>::remove(&x.owner);
+							let new_total_staked =
+								<Total<T>>::get().saturating_sub(state.total_backing);
 							<Total<T>>::put(new_total_staked);
 							Self::deposit_event(Event::CollatorLeft(
 								x.owner,
-								state.total,
+								state.total_backing,
 								new_total_staked,
 							));
 						}
@@ -1393,7 +1645,7 @@ pub mod pallet {
 			let (mut all_collators, mut total) = (0u32, BalanceOf::<T>::zero());
 			let mut candidates = <CandidatePool<T>>::get().0;
 			// order candidates by stake (least to greatest so requires `rev()`)
-			candidates.sort_unstable_by(|a, b| a.amount.partial_cmp(&b.amount).unwrap());
+			candidates.sort_unstable_by(|a, b| a.amount.cmp(&b.amount));
 			let top_n = <TotalSelected<T>>::get() as usize;
 			// choose the top TotalSelected qualified candidates, ordered by stake
 			let mut collators = candidates
@@ -1405,9 +1657,9 @@ pub mod pallet {
 				.collect::<Vec<T::AccountId>>();
 			// snapshot exposure for round for weighting reward distribution
 			for account in collators.iter() {
-				let state = <CollatorState<T>>::get(&account)
+				let state = <CollatorState2<T>>::get(&account)
 					.expect("all members of CandidateQ must be candidates");
-				let amount = state.total;
+				let amount = state.total_counted;
 				let exposure: CollatorSnapshot<T::AccountId, BalanceOf<T>> = state.into();
 				<AtStake<T>>::insert(next, account, exposure);
 				all_collators += 1u32;
```

### pallets/parachain-staking/src/tests.rs
```diff
@@ -19,7 +19,7 @@ use crate::mock::{
 	events, last_event, roll_to, set_author, Balances, Event as MetaEvent, ExtBuilder, Origin,
 	Stake, System, Test,
 };
-use crate::{CollatorStatus, Error, Event, Range};
+use crate::{CollatorStatus, Error, Event, NominatorAdded, Range};
 use frame_support::{assert_noop, assert_ok};
 use sp_runtime::{traits::Zero, DispatchError, Perbill, Percent};
 
@@ -172,7 +172,7 @@ fn collator_exit_executes_after_delay() {
 				last_event(),
 				MetaEvent::stake(Event::CollatorScheduledExit(3, 2, 5))
 			);
-			let info = Stake::collator_state(&2).unwrap();
+			let info = Stake::collator_state2(&2).unwrap();
 			assert_eq!(info.state, CollatorStatus::Leaving(5));
 			roll_to(21);
 			// we must exclude leaving collators from rewards while
@@ -500,8 +500,8 @@ fn collator_commission() {
 			roll_to(11);
 			let mut new = vec![
 				Event::JoinedCollatorCandidates(4, 20, 60),
-				Event::Nomination(5, 10, 4, 30),
-				Event::Nomination(6, 10, 4, 40),
+				Event::Nomination(5, 10, 4, NominatorAdded::AddedToTop { new_total: 30 }),
+				Event::Nomination(6, 10, 4, NominatorAdded::AddedToTop { new_total: 40 }),
 				Event::CollatorChosen(3, 4, 40),
 				Event::CollatorChosen(3, 1, 40),
 				Event::NewRound(10, 3, 2, 80),
@@ -518,8 +518,8 @@ fn collator_commission() {
 				Event::CollatorChosen(4, 1, 40),
 				Event::NewRound(15, 4, 2, 80),
 				Event::Rewarded(4, 18),
-				Event::Rewarded(5, 6),
 				Event::Rewarded(6, 6),
+				Event::Rewarded(5, 6),
 				Event::CollatorChosen(5, 4, 40),
 				Event::CollatorChosen(5, 1, 40),
 				Event::NewRound(20, 5, 2, 80),
@@ -582,9 +582,9 @@ fn multiple_nominations() {
 			);
 			roll_to(16);
 			let mut new = vec![
-				Event::Nomination(6, 10, 2, 50),
-				Event::Nomination(6, 10, 3, 30),
-				Event::Nomination(6, 10, 4, 30),
+				Event::Nomination(6, 10, 2, NominatorAdded::AddedToTop { new_total: 50 }),
+				Event::Nomination(6, 10, 3, NominatorAdded::AddedToTop { new_total: 30 }),
+				Event::Nomination(6, 10, 4, NominatorAdded::AddedToTop { new_total: 30 }),
 				Event::CollatorChosen(3, 2, 50),
 				Event::CollatorChosen(3, 1, 50),
 				Event::CollatorChosen(3, 4, 30),
@@ -611,10 +611,7 @@ fn multiple_nominations() {
 					message: Some("InsufficientBalance")
 				},
 			);
-			assert_noop!(
-				Stake::nominate(Origin::signed(10), 2, 10),
-				Error::<Test>::TooManyNominators
-			);
+			assert_ok!(Stake::nominate(Origin::signed(10), 2, 10),);
 			roll_to(26);
 			let mut new2 = vec![
 				Event::CollatorChosen(5, 2, 50),
@@ -623,7 +620,8 @@ fn multiple_nominations() {
 				Event::CollatorChosen(5, 3, 30),
 				Event::CollatorChosen(5, 5, 10),
 				Event::NewRound(20, 5, 5, 170),
-				Event::Nomination(7, 80, 2, 130),
+				Event::Nomination(7, 80, 2, NominatorAdded::AddedToTop { new_total: 130 }),
+				Event::Nomination(10, 10, 2, NominatorAdded::AddedToBottom),
 				Event::CollatorChosen(6, 2, 130),
 				Event::CollatorChosen(6, 1, 50),
 				Event::CollatorChosen(6, 4, 30),
@@ -953,9 +951,9 @@ fn payouts_follow_nomination_changes() {
 				Event::CollatorChosen(3, 5, 10),
 				Event::NewRound(10, 3, 5, 140),
 				Event::Rewarded(1, 26),
-				Event::Rewarded(6, 8),
 				Event::Rewarded(7, 8),
 				Event::Rewarded(10, 8),
+				Event::Rewarded(6, 8),
 				Event::CollatorChosen(4, 1, 50),
 				Event::CollatorChosen(4, 2, 40),
 				Event::CollatorChosen(4, 4, 20),
@@ -980,9 +978,9 @@ fn payouts_follow_nomination_changes() {
 				Event::NominatorLeftCollator(6, 1, 10, 40),
 				Event::NominatorLeft(6, 10),
 				Event::Rewarded(1, 27),
-				Event::Rewarded(6, 8),
 				Event::Rewarded(7, 8),
 				Event::Rewarded(10, 8),
+				Event::Rewarded(6, 8),
 				Event::CollatorChosen(5, 2, 40),
 				Event::CollatorChosen(5, 1, 40),
 				Event::CollatorChosen(5, 4, 20),
@@ -998,9 +996,9 @@ fn payouts_follow_nomination_changes() {
 			// keep paying 6
 			let mut new3 = vec![
 				Event::Rewarded(1, 29),
-				Event::Rewarded(6, 9),
 				Event::Rewarded(7, 9),
 				Event::Rewarded(10, 9),
+				Event::Rewarded(6, 9),
 				Event::CollatorChosen(6, 2, 40),
 				Event::CollatorChosen(6, 1, 40),
 				Event::CollatorChosen(6, 4, 20),
@@ -1031,7 +1029,7 @@ fn payouts_follow_nomination_changes() {
 			roll_to(36);
 			// new nomination is not rewarded yet
 			let mut new5 = vec![
-				Event::Nomination(8, 10, 1, 50),
+				Event::Nomination(8, 10, 1, NominatorAdded::AddedToTop { new_total: 50 }),
 				Event::Rewarded(1, 36),
 				Event::Rewarded(7, 12),
 				Event::Rewarded(10, 12),
@@ -1079,6 +1077,290 @@ fn payouts_follow_nomination_changes() {
 		});
 }
 
+#[test]
+// MaxNominatorsPerCollator = 4
+fn bottom_nominations_are_empty_when_top_nominations_not_full() {
+	ExtBuilder::default()
+		.with_balances(vec![(1, 20), (2, 10), (3, 10), (4, 10), (5, 10)])
+		.with_collators(vec![(1, 20)])
+		.build()
+		.execute_with(|| {
+			// no top nominators => no bottom nominators
+			let collator_state = Stake::collator_state2(1).unwrap();
+			assert!(collator_state.top_nominators.is_empty());
+			assert!(collator_state.bottom_nominators.is_empty());
+			// 1 nominator => 1 top nominator, 0 bottom nominators
+			assert_ok!(Stake::nominate(Origin::signed(2), 1, 10));
+			let collator_state = Stake::collator_state2(1).unwrap();
+			assert!(collator_state.top_nominators.len() == 1usize);
+			assert!(collator_state.bottom_nominators.is_empty());
+			// 2 nominators => 2 top nominators, 0 bottom nominators
+			assert_ok!(Stake::nominate(Origin::signed(3), 1, 10));
+			let collator_state = Stake::collator_state2(1).unwrap();
+			assert!(collator_state.top_nominators.len() == 2usize);
+			assert!(collator_state.bottom_nominators.is_empty());
+			// 3 nominators => 3 top nominators, 0 bottom nominators
+			assert_ok!(Stake::nominate(Origin::signed(4), 1, 10));
+			let collator_state = Stake::collator_state2(1).unwrap();
+			assert!(collator_state.top_nominators.len() == 3usize);
+			assert!(collator_state.bottom_nominators.is_empty());
+			// 4 nominators => 4 top nominators, 0 bottom nominators
+			assert_ok!(Stake::nominate(Origin::signed(5), 1, 10));
+			let collator_state = Stake::collator_state2(1).unwrap();
+			assert!(collator_state.top_nominators.len() == 4usize);
+			assert!(collator_state.bottom_nominators.is_empty());
+		});
+}
+
+#[test]
+// MaxNominatorsPerCollator = 4
+fn candidate_pool_updates_when_total_counted_changes() {
+	ExtBuilder::default()
+		.with_balances(vec![
+			(1, 20),
+			(3, 19),
+			(4, 20),
+			(5, 21),
+			(6, 22),
+			(7, 15),
+			(8, 16),
+			(9, 17),
+			(10, 18),
+		])
+		.with_collators(vec![(1, 20)])
+		.with_nominations(vec![
+			(3, 1, 11),
+			(4, 1, 12),
+			(5, 1, 13),
+			(6, 1, 14),
+			(7, 1, 15),
+			(8, 1, 16),
+			(9, 1, 17),
+			(10, 1, 18),
+		])
+		.build()
+		.execute_with(|| {
+			fn is_candidate_pool_bond(account: u64, bond: u128) {
+				let pool = Stake::candidate_pool();
+				for candidate in pool.0 {
+					if candidate.owner == account {
+						assert_eq!(candidate.amount, bond);
+					}
+				}
+			}
+			// 15 + 16 + 17 + 18 + 20 = 86 (top 4 + self bond)
+			is_candidate_pool_bond(1, 86);
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(3), 1, 8));
+			// 16 + 17 + 18 + 19 + 20 = 90 (top 4 + self bond)
+			is_candidate_pool_bond(1, 90);
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(4), 1, 8));
+			// 17 + 18 + 19 + 20 + 20 = 94 (top 4 + self bond)
+			is_candidate_pool_bond(1, 94);
+			assert_ok!(Stake::nominator_bond_less(Origin::signed(10), 1, 3));
+			// 16 + 17 + 19 + 20 + 20 = 92 (top 4 + self bond)
+			is_candidate_pool_bond(1, 92);
+			assert_ok!(Stake::nominator_bond_less(Origin::signed(9), 1, 4));
+			// 15 + 16 + 19 + 20 + 20 = 90 (top 4 + self bond)
+			is_candidate_pool_bond(1, 90);
+		});
+}
+
+#[test]
+// MaxNominatorsPerCollator = 4
+fn only_top_collators_are_counted() {
+	ExtBuilder::default()
+		.with_balances(vec![
+			(1, 20),
+			(3, 19),
+			(4, 20),
+			(5, 21),
+			(6, 22),
+			(7, 15),
+			(8, 16),
+			(9, 17),
+			(10, 18),
+		])
+		.with_collators(vec![(1, 20)])
+		.with_nominations(vec![
+			(3, 1, 11),
+			(4, 1, 12),
+			(5, 1, 13),
+			(6, 1, 14),
+			(7, 1, 15),
+			(8, 1, 16),
+			(9, 1, 17),
+			(10, 1, 18),
+		])
+		.build()
+		.execute_with(|| {
+			// sanity check that 3-10 are nominators immediately
+			for i in 3..11 {
+				assert!(Stake::is_nominator(&i));
+			}
+			let mut expected_events = Vec::new();
+			let collator_state = Stake::collator_state2(1).unwrap();
+			// 15 + 16 + 17 + 18 + 20 = 86 (top 4 + self bond)
+			assert_eq!(collator_state.total_counted, 86);
+			// 11 + 12 + 13 + 14 = 50
+			assert_eq!(
+				collator_state.total_counted + 50,
+				collator_state.total_backing
+			);
+			// bump bottom to the top
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(3), 1, 8));
+			expected_events.push(Event::NominationIncreased(3, 1, 86, true, 90));
+			assert_eq!(events(), expected_events);
+			let collator_state = Stake::collator_state2(1).unwrap();
+			// 16 + 17 + 18 + 19 + 20 = 90 (top 4 + self bond)
+			assert_eq!(collator_state.total_counted, 90);
+			// 12 + 13 + 14 + 15 = 54
+			assert_eq!(
+				collator_state.total_counted + 54,
+				collator_state.total_backing
+			);
+			// bump bottom to the top
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(4), 1, 8));
+			expected_events.push(Event::NominationIncreased(4, 1, 90, true, 94));
+			assert_eq!(events(), expected_events);
+			let collator_state = Stake::collator_state2(1).unwrap();
+			// 17 + 18 + 19 + 20 + 20 = 94 (top 4 + self bond)
+			assert_eq!(collator_state.total_counted, 94);
+			// 13 + 14 + 15 + 16 = 58
+			assert_eq!(
+				collator_state.total_counted + 58,
+				collator_state.total_backing
+			);
+			// bump bottom to the top
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(5), 1, 8));
+			expected_events.push(Event::NominationIncreased(5, 1, 94, true, 98));
+			assert_eq!(events(), expected_events);
+			let collator_state = Stake::collator_state2(1).unwrap();
+			// 18 + 19 + 20 + 21 + 20 = 98 (top 4 + self bond)
+			assert_eq!(collator_state.total_counted, 98);
+			// 14 + 15 + 16 + 17 = 62
+			assert_eq!(
+				collator_state.total_counted + 62,
+				collator_state.total_backing
+			);
+			// bump bottom to the top
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(6), 1, 8));
+			expected_events.push(Event::NominationIncreased(6, 1, 98, true, 102));
+			assert_eq!(events(), expected_events);
+			let collator_state = Stake::collator_state2(1).unwrap();
+			// 19 + 20 + 21 + 22 + 20 = 102 (top 4 + self bond)
+			assert_eq!(collator_state.total_counted, 102);
+			// 15 + 16 + 17 + 18 = 66
+			assert_eq!(
+				collator_state.total_counted + 66,
+				collator_state.total_backing
+			);
+		});
+}
+
+#[test]
+fn nomination_events_convey_correct_position() {
+	ExtBuilder::default()
+		.with_balances(vec![
+			(1, 100),
+			(2, 100),
+			(3, 100),
+			(4, 100),
+			(5, 100),
+			(6, 100),
+			(7, 100),
+			(8, 100),
+			(9, 100),
+			(10, 100),
+		])
+		.with_collators(vec![(1, 20), (2, 20)])
+		.with_nominations(vec![(3, 1, 11), (4, 1, 12), (5, 1, 13), (6, 1, 14)])
+		.build()
+		.execute_with(|| {
+			let collator1_state = Stake::collator_state2(1).unwrap();
+			// 11 + 12 + 13 + 14 + 20 = 70 (top 4 + self bond)
+			assert_eq!(collator1_state.total_counted, 70);
+			assert_eq!(collator1_state.total_counted, collator1_state.total_backing);
+			// Top nominations are full, new highest nomination is made
+			assert_ok!(Stake::nominate(Origin::signed(7), 1, 15));
+			let mut expected_events = Vec::new();
+			expected_events.push(Event::Nomination(
+				7,
+				15,
+				1,
+				NominatorAdded::AddedToTop { new_total: 74 },
+			));
+			assert_eq!(events(), expected_events);
+			let collator1_state = Stake::collator_state2(1).unwrap();
+			// 12 + 13 + 14 + 15 + 20 = 70 (top 4 + self bond)
+			assert_eq!(collator1_state.total_counted, 74);
+			// 11 = 11
+			assert_eq!(
+				collator1_state.total_counted + 11,
+				collator1_state.total_backing
+			);
+			// New nomination is added to the bottom
+			assert_ok!(Stake::nominate(Origin::signed(8), 1, 10));
+			expected_events.push(Event::Nomination(8, 10, 1, NominatorAdded::AddedToBottom));
+			assert_eq!(events(), expected_events);
+			let collator1_state = Stake::collator_state2(1).unwrap();
+			// 12 + 13 + 14 + 15 + 20 = 70 (top 4 + self bond)
+			assert_eq!(collator1_state.total_counted, 74);
+			// 10 + 11 = 21
+			assert_eq!(
+				collator1_state.total_counted + 21,
+				collator1_state.total_backing
+			);
+			// 8 increases nomination to the top
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(8), 1, 3));
+			expected_events.push(Event::NominationIncreased(8, 1, 74, true, 75));
+			assert_eq!(events(), expected_events);
+			let collator1_state = Stake::collator_state2(1).unwrap();
+			// 13 + 13 + 14 + 15 + 20 = 75 (top 4 + self bond)
+			assert_eq!(collator1_state.total_counted, 75);
+			// 11 + 12 = 23
+			assert_eq!(
+				collator1_state.total_counted + 23,
+				collator1_state.total_backing
+			);
+			// 3 increases nomination but stays in bottom
+			assert_ok!(Stake::nominator_bond_more(Origin::signed(3), 1, 1));
+			expected_events.push(Event::NominationIncreased(3, 1, 75, false, 75));
+			assert_eq!(events(), expected_events);
+			let collator1_state = Stake::collator_state2(1).unwrap();
+			// 13 + 13 + 14 + 15 + 20 = 75 (top 4 + self bond)
+			assert_eq!(collator1_state.total_counted, 75);
+			// 12 + 12 = 24
+			assert_eq!(
+				collator1_state.total_counted + 24,
+				collator1_state.total_backing
+			);
+			// 6 decreases nomination but stays in top
+			assert_ok!(Stake::nominator_bond_less(Origin::signed(6), 1, 2));
+			expected_events.push(Event::NominationDecreased(6, 1, 75, true, 73));
+			assert_eq!(events(), expected_events);
+			let collator1_state = Stake::collator_state2(1).unwrap();
+			// 12 + 13 + 13 + 15 + 20 = 73 (top 4 + self bond)
+			assert_eq!(collator1_state.total_counted, 73);
+			// 12 + 12 = 24
+			assert_eq!(
+				collator1_state.total_counted + 24,
+				collator1_state.total_backing
+			);
+			// 6 decreases nomination and is bumped to bottom
+			assert_ok!(Stake::nominator_bond_less(Origin::signed(6), 1, 1));
+			expected_events.push(Event::NominationDecreased(6, 1, 73, false, 73));
+			assert_eq!(events(), expected_events);
+			let collator1_state = Stake::collator_state2(1).unwrap();
+			// 12 + 13 + 13 + 15 + 20 = 73 (top 4 + self bond)
+			assert_eq!(collator1_state.total_counted, 73);
+			// 11 + 12 = 23
+			assert_eq!(
+				collator1_state.total_counted + 23,
+				collator1_state.total_backing
+			);
+		});
+}
+
 #[test]
 fn parachain_bond_reserve_works() {
 	ExtBuilder::default()
@@ -1135,9 +1417,9 @@ fn parachain_bond_reserve_works() {
 				Event::NewRound(10, 3, 5, 140),
 				Event::ReservedForParachainBond(11, 15),
 				Event::Rewarded(1, 18),
-				Event::Rewarded(6, 6),
 				Event::Rewarded(7, 6),
 				Event::Rewarded(10, 6),
+				Event::Rewarded(6, 6),
 				Event::CollatorChosen(4, 1, 50),
 				Event::CollatorChosen(4, 2, 40),
 				Event::CollatorChosen(4, 4, 20),
@@ -1164,9 +1446,9 @@ fn parachain_bond_reserve_works() {
 				Event::NominatorLeft(6, 10),
 				Event::ReservedForParachainBond(11, 16),
 				Event::Rewarded(1, 19),
-				Event::Rewarded(6, 6),
 				Event::Rewarded(7, 6),
 				Event::Rewarded(10, 6),
+				Event::Rewarded(6, 6),
 				Event::CollatorChosen(5, 2, 40),
 				Event::CollatorChosen(5, 1, 40),
 				Event::CollatorChosen(5, 4, 20),
@@ -1192,9 +1474,9 @@ fn parachain_bond_reserve_works() {
 				),
 				Event::ReservedForParachainBond(11, 27),
 				Event::Rewarded(1, 15),
-				Event::Rewarded(6, 4),
 				Event::Rewarded(7, 4),
 				Event::Rewarded(10, 4),
+				Event::Rewarded(6, 4),
 				Event::CollatorChosen(6, 2, 40),
 				Event::CollatorChosen(6, 1, 40),
 				Event::CollatorChosen(6, 4, 20),
@@ -1228,7 +1510,7 @@ fn parachain_bond_reserve_works() {
 			roll_to(36);
 			// new nomination is not rewarded yet
 			let mut new5 = vec![
-				Event::Nomination(8, 10, 1, 50),
+				Event::Nomination(8, 10, 1, NominatorAdded::AddedToTop { new_total: 50 }),
 				Event::ReservedForParachainBond(11, 30),
 				Event::Rewarded(1, 18),
 				Event::Rewarded(7, 6),
```

### runtime/moonbase/src/lib.rs
```diff
@@ -125,7 +125,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
 	spec_name: create_runtime_str!("moonbase"),
 	impl_name: create_runtime_str!("moonbase"),
 	authoring_version: 3,
-	spec_version: 50,
+	spec_version: 51,
 	impl_version: 0,
 	apis: RUNTIME_API_VERSIONS,
 	transaction_version: 2,
```

### runtime/moonbase/tests/integration_test.rs
```diff
@@ -27,7 +27,7 @@ use moonbase_runtime::{
 };
 use nimbus_primitives::NimbusId;
 use pallet_evm::PrecompileSet;
-use parachain_staking::Bond;
+use parachain_staking::{Bond, NominatorAdded};
 use sp_core::{Public, H160, U256};
 use sp_runtime::DispatchError;
 
@@ -715,7 +715,9 @@ fn nominate_via_precompile() {
 					AccountId::from(BOB),
 					1000 * UNITS,
 					AccountId::from(ALICE),
-					2000 * UNITS,
+					NominatorAdded::AddedToTop {
+						new_total: 2000 * UNITS,
+					},
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
 					staking_precompile_address,
@@ -948,6 +950,7 @@ fn nominator_bond_more_less_via_precompile() {
 					AccountId::from(BOB),
 					AccountId::from(ALICE),
 					1_500 * UNITS,
+					true,
 					2_000 * UNITS,
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
@@ -991,6 +994,7 @@ fn nominator_bond_more_less_via_precompile() {
 					AccountId::from(BOB),
 					AccountId::from(ALICE),
 					2_000 * UNITS,
+					true,
 					1_500 * UNITS,
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
```

### runtime/moonbeam/src/lib.rs
```diff
@@ -124,7 +124,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
 	spec_name: create_runtime_str!("moonbeam"),
 	impl_name: create_runtime_str!("moonbeam"),
 	authoring_version: 3,
-	spec_version: 51,
+	spec_version: 52,
 	impl_version: 0,
 	apis: RUNTIME_API_VERSIONS,
 	transaction_version: 2,
```

### runtime/moonbeam/tests/integration_test.rs
```diff
@@ -29,7 +29,7 @@ use moonbeam_runtime::{
 };
 use nimbus_primitives::NimbusId;
 use pallet_evm::PrecompileSet;
-use parachain_staking::Bond;
+use parachain_staking::{Bond, NominatorAdded};
 use precompiles::MoonbeamPrecompiles;
 use sp_core::{Public, H160, U256};
 use sp_runtime::DispatchError;
@@ -708,7 +708,9 @@ fn nominate_via_precompile() {
 					AccountId::from(BOB),
 					1000 * GLMR,
 					AccountId::from(ALICE),
-					2000 * GLMR,
+					NominatorAdded::AddedToTop {
+						new_total: 2000 * GLMR,
+					},
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
 					staking_precompile_address,
@@ -933,6 +935,7 @@ fn nominator_bond_more_less_via_precompile() {
 					AccountId::from(BOB),
 					AccountId::from(ALICE),
 					1_500 * GLMR,
+					true,
 					2_000 * GLMR,
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
@@ -976,6 +979,7 @@ fn nominator_bond_more_less_via_precompile() {
 					AccountId::from(BOB),
 					AccountId::from(ALICE),
 					2_000 * GLMR,
+					true,
 					1_500 * GLMR,
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
```

### runtime/moonriver/src/lib.rs
```diff
@@ -126,8 +126,8 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
 	spec_name: create_runtime_str!("moonriver"),
 	impl_name: create_runtime_str!("moonriver"),
 	authoring_version: 3,
-	spec_version: 51,
-	impl_version: 2,
+	spec_version: 52,
+	impl_version: 0,
 	apis: RUNTIME_API_VERSIONS,
 	transaction_version: 2,
 };
```

### runtime/moonriver/tests/integration_test.rs
```diff
@@ -25,7 +25,7 @@ use evm::{executor::PrecompileOutput, Context, ExitSucceed};
 use frame_support::{assert_noop, assert_ok, dispatch::Dispatchable, traits::fungible::Inspect};
 use nimbus_primitives::NimbusId;
 use pallet_evm::PrecompileSet;
-use parachain_staking::Bond;
+use parachain_staking::{Bond, NominatorAdded};
 use precompiles::MoonbeamPrecompiles;
 use sp_core::{Public, H160, U256};
 use sp_runtime::DispatchError;
@@ -704,7 +704,9 @@ fn nominate_via_precompile() {
 					AccountId::from(BOB),
 					1000 * MOVR,
 					AccountId::from(ALICE),
-					2000 * MOVR,
+					NominatorAdded::AddedToTop {
+						new_total: 2000 * MOVR,
+					},
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
 					staking_precompile_address,
@@ -929,6 +931,7 @@ fn nominator_bond_more_less_via_precompile() {
 					AccountId::from(BOB),
 					AccountId::from(ALICE),
 					1_500 * MOVR,
+					true,
 					2_000 * MOVR,
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
@@ -972,6 +975,7 @@ fn nominator_bond_more_less_via_precompile() {
 					AccountId::from(BOB),
 					AccountId::from(ALICE),
 					2_000 * MOVR,
+					true,
 					1_500 * MOVR,
 				)),
 				Event::pallet_evm(pallet_evm::Event::<Runtime>::Executed(
```

### runtime/moonshadow/src/lib.rs
```diff
@@ -123,7 +123,7 @@ pub const VERSION: RuntimeVersion = RuntimeVersion {
 	spec_name: create_runtime_str!("moonshadow"),
 	impl_name: create_runtime_str!("moonshadow"),
 	authoring_version: 3,
-	spec_version: 51,
+	spec_version: 52,
 	impl_version: 0,
 	apis: RUNTIME_API_VERSIONS,
 	transaction_version: 2,
```
