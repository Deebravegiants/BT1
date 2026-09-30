# [?] Merge bitcoin/bitcoin#34085: cluster mempool: exploit SFL properties in txgraph

## Summary
Severity: Unknown
Chain: Bitcoin
Component: bitcoin/bitcoin
Published: 2026-01-06
Source: https://github.com/bitcoin/bitcoin/commit/c60f9cb66ee78ffb2cf8b9bedafddfc35a7df186
Type: security-commit

## Details
Merge bitcoin/bitcoin#34085: cluster mempool: exploit SFL properties in txgraph

1808b5aaf7c4910122fcd088e03d790189907438 clusterlin: remove unused FixLinearization (cleanup) (Pieter Wuille)
34a77138b7a6f65a31c6273f2770e943cc0b474b txgraph: permit non-topological clusters to defer fixing (optimization) (Pieter Wuille)
3380e0cbb59b2a893faabfa8f9aa18e582a11c2f txgraph: use PostLinearize less prior to linearizing (Pieter Wuille)
62dd88624a7fba14d2dac32d94fd101eb378d1e7 txgraph: drop NEEDS_SPLIT_ACCEPTABLE (simplification) (Pieter Wuille)
01ffcf464a4679136185e323b5b0328695a5bd1e clusterlin: support fixing linearizations (feature) (Pieter Wuille)

Pull request description:

  Part of #30289, follow-up to #32545.

  This gets rid of `FixLinearization()` by integrating the functionality into `Linearize()`, and makes txgraph exploit that (by delaying fixing of clusters until their first re-linearization). It also reduces (but does not eliminate) the number of calls to `PostLinearize`, as the SFL linearization effectively performs something very similar to postlinearization when loading in an existing linearization already.

ACKs for top commit:
  instagibbs:
    reACK 1808b5aaf7c4910122fcd088e03d790189907438
  marcofleon:
    code review ACK 1808b5aaf7c4910122fcd088e03d790189907438

Tree-SHA512: 81cd9549de2968f5126079cbb532e2cb052ea8157c9c9ce37fd39ad2294105d7c79ee8d946c3d8f7af5b2119299a232c448b42a33e1e43ccc778a5b52957e387

## Patch
### src/cluster_linearize.h
```diff
@@ -1338,8 +1338,9 @@ class SpanningForestState
  * @param[in] rng_seed            A random number seed to control search order. This prevents peers
  *                                from predicting exactly which clusters would be hard for us to
  *                                linearize.
- * @param[in] old_linearization   An existing linearization for the cluster (which must be
- *                                topologically valid), or empty.
+ * @param[in] old_linearization   An existing linearization for the cluster, or empty.
+ * @param[in] is_topological      (Only relevant if old_linearization is not empty) Whether
+ *                                old_linearization is topologically valid.
  * @return                        A tuple of:
  *                                - The resulting linearization. It is guaranteed to be at least as
  *                                  good (in the feerate diagram sense) as old_linearization.
@@ -1348,12 +1349,13 @@ class SpanningForestState
  *                                - How many optimization steps were actually performed.
  */
 template<typename SetType>
-std::tuple<std::vector<DepGraphIndex>, bool, uint64_t> Linearize(const DepGraph<SetType>& depgraph, uint64_t max_iterations, uint64_t rng_seed, std::span<const DepGraphIndex> old_linearization = {}) noexcept
+std::tuple<std::vector<DepGraphIndex>, bool, uint64_t> Linearize(const DepGraph<SetType>& depgraph, uint64_t max_iterations, uint64_t rng_seed, std::span<const DepGraphIndex> old_linearization = {}, bool is_topological = true) noexcept
 {
     /** Initialize a spanning forest data structure for this cluster. */
     SpanningForestState forest(depgraph, rng_seed);
     if (!old_linearization.empty()) {
         forest.LoadLinearization(old_linearization);
+        if (!is_topological) forest.MakeTopological();
     } else {
         forest.MakeTopological();
     }
@@ -1573,38 +1575,6 @@ void PostLinearize(const DepGraph<SetType>& depgraph, std::span<DepGraphIndex> l
     }
 }
 
-/** Make linearization topological, retaining its ordering where possible. */
-template<typename SetType>
-void FixLinearization(const DepGraph<SetType>& depgraph, std::span<DepGraphIndex> linearization) noexcept
-{
-    // This algorithm can be summarized as moving every element in the linearization backwards
-    // until it is placed after all its ancestors.
-    SetType done;
-    const auto len = linearization.size();
-    // Iterate over the elements of linearization from back to front (i is distance from back).
-    for (DepGraphIndex i = 0; i < len; ++i) {
-        /** The element at that position. */
-        DepGraphIndex elem = linearization[len - 1 - i];
-        /** j represents how far from the back of the linearization elem should be placed. */
-        DepGraphIndex j = i;
-        // Figure out which elements need to be moved before elem.
-        SetType place_before = done & depgraph.Ancestors(elem);
-        // Find which position to place elem in (updating j), continuously moving the elements
-        // in between forward.
-        while (place_before.Any()) {
-            // j cannot be 0 here; if it was, then there was necessarily nothing earlier which
-            // elem needs to be placed before anymore, and place_before would be empty.
-            Assume(j > 0);
-            auto to_swap = linearization[len - 1 - (j - 1)];
-            place_before.Reset(to_swap);
-            linearization[len - 1 - (j--)] = to_swap;
-        }
-        // Put elem in its final position and mark it as done.
-        linearization[len - 1 - j] = elem;
-        done.Set(elem);
-    }
-}
-
 } // namespace cluster_linearize
 
 #endif // BITCOIN_CLUSTER_LINEARIZE_H
```

### src/test/cluster_linearize_tests.cpp
```diff
@@ -68,7 +68,8 @@ void TestOptimalLinearization(const std::vector<uint8_t>& enc, const std::vector
         for (int iter = 0; iter < 200; ++iter) {
             bool opt;
             uint64_t cost{0};
-            switch (rng.randrange(3)) {
+            bool is_topological{true};
+            switch (rng.randrange(4)) {
             case 0:
                 // Use empty input linearization.
                 lin.clear();
@@ -77,12 +78,17 @@ void TestOptimalLinearization(const std::vector<uint8_t>& enc, const std::vector
                 // Reuse previous optimal linearization as input.
                 break;
             case 2:
-                // Construct random input linearization.
+                // Construct random valid input linearization.
                 std::shuffle(lin.begin(), lin.end(), rng);
-                FixLinearization(depgraph, lin);
+                std::sort(lin.begin(), lin.end(), [&](auto a, auto b) { return depgraph.Ancestors(a).Count() < depgraph.Ancestors(b).Count(); });
+                break;
+            case 3:
+                // Construct random potentially invalid input linearization.
+                std::shuffle(lin.begin(), lin.end(), rng);
+                is_topological = false;
                 break;
             }
-            std::tie(lin, opt, cost) = Linearize(depgraph, 1000000000000, rng.rand64(), lin);
+            std::tie(lin, opt, cost) = Linearize(depgraph, 1000000000000, rng.rand64(), lin, is_topological);
             BOOST_CHECK(opt);
             BOOST_CHECK(cost <= MaxOptimalLinearizationIters(depgraph.TxCount()));
             SanityCheck(depgraph, lin);
```

### src/test/fuzz/cluster_linearize.cpp
```diff
@@ -58,8 +58,6 @@
  *   - clusterlin_postlinearize
  *   - clusterlin_postlinearize_tree
  *   - clusterlin_postlinearize_moved_leaf
- * - FixLinearization tests:
- *   - clusterlin_fix_linearization
  * - MakeConnected tests (a test-only function):
  *   - clusterlin_make_connected
  */
@@ -998,35 +996,40 @@ FUZZ_TARGET(clusterlin_linearize)
     DepGraph<TestBitSet> depgraph;
     uint64_t rng_seed{0};
     uint64_t iter_count{0};
-    uint8_t make_connected{1};
+    uint8_t flags{7};
     try {
-        reader >> VARINT(iter_count) >> Using<DepGraphFormatter>(depgraph) >> rng_seed >> make_connected;
+        reader >> VARINT(iter_count) >> Using<DepGraphFormatter>(depgraph) >> rng_seed >> flags;
     } catch (const std::ios_base::failure&) {}
+    bool make_connected = flags & 1;
+    // The following 3 booleans have 4 combinations:
+    // - (flags & 6) == 0: do not provide input linearization.
+    // - (flags & 6) == 2: provide potentially non-topological input.
+    // - (flags & 6) == 4: provide topological input linearization, but do not claim it is
+    //                     topological.
+    // - (flags & 6) == 6: provide topological input linearization, and claim it is topological.
+    bool provide_input = flags & 6;
+    bool provide_topological_input = flags & 4;
+    bool claim_topological_input = (flags & 6) == 6;
     // The most complicated graphs are connected ones (other ones just split up). Optionally force
     // the graph to be connected.
     if (make_connected) MakeConnected(depgraph);
 
     // Optionally construct an old linearization for it.
     std::vector<DepGraphIndex> old_linearization;
-    {
-        uint8_t have_old_linearization{0};
-        try {
-            reader >> have_old_linearization;
-        } catch(const std::ios_base::failure&) {}
-        if (have_old_linearization & 1) {
-            old_linearization = ReadLinearization(depgraph, reader);
-            SanityCheck(depgraph, old_linearization);
-        }
+    if (provide_input) {
+        old_linearization = ReadLinearization(depgraph, reader, /*topological=*/provide_topological_input);
+        if (provide_topological_input) SanityCheck(depgraph, old_linearization);
     }
 
     // Invoke Linearize().
     iter_count &= 0x7ffff;
-    auto [linearization, optimal, cost] = Linearize(depgraph, iter_count, rng_seed, old_linearization);
+    auto [linearization, optimal, cost] = Linearize(depgraph, iter_count, rng_seed, old_linearization, /*is_topological=*/claim_topological_input);
     SanityCheck(depgraph, linearization);
     auto chunking = ChunkLinearization(depgraph, linearization);
 
-    // Linearization must always be as good as the old one, if provided.
-    if (!old_linearization.empty()) {
+    // Linearization must always be as good as the old one, if provided and topological (even when
+    // not claimed to be topological).
+    if (provide_topological_input) {
         auto old_chunking = ChunkLinearization(depgraph, old_linearization);
         auto cmp = CompareChunks(chunking, old_chunking);
         assert(cmp >= 0);
@@ -1197,46 +1200,3 @@ FUZZ_TARGET(clusterlin_postlinearize_moved_leaf)
     auto cmp = CompareChunks(new_chunking, old_chunking);
     assert(cmp >= 0);
 }
-
-FUZZ_TARGET(clusterlin_fix_linearization)
-{
-    // Verify expected properties of FixLinearization() on arbitrary linearizations.
-
-    // Retrieve a depgraph from the fuzz input.
-    SpanReader reader(buffer);
-    DepGraph<TestBitSet> depgraph;
-    try {
-        reader >> Using<DepGraphFormatter>(depgraph);
-    } catch (const std::ios_base::failure&) {}
-
-    // Construct an arbitrary linearization (not necessarily topological for depgraph).
-    std::vector<DepGraphIndex> linearization = ReadLinearization(depgraph, reader, /*topological=*/false);
-    assert(linearization.size() == depgraph.TxCount());
-
-    // Determine what prefix of linearization is topological, i.e., the position of the first entry
-    // in linearization which corresponds to a transaction that is not preceded by all its
-    // ancestors.
-    size_t topo_prefix = 0;
-    auto todo = depgraph.Positions();
-    while (topo_prefix < linearization.size()) {
-        DepGraphIndex idx = linearization[topo_prefix];
-        todo.Reset(idx);
-        if (todo.Overlaps(depgraph.Ancestors(idx))) break;
-        ++topo_prefix;
-    }
-
-    // Then make a fixed copy of linearization.
-    auto linearization_fixed = linearization;
-    FixLinearization(depgraph, linearization_fixed);
-    // Sanity check it (which includes testing whether it is topological).
-    SanityCheck(depgraph, linearization_fixed);
-
-    // FixLinearization does not modify the topological prefix of linearization.
-    assert(std::equal(linearization.begin(), linearization.begin() + topo_prefix,
-                      linearization_fixed.begin()));
-    // This also means that if linearization was entirely topological, FixLinearization cannot have
-    // modified it. This is implied by the assertion above already, but repeat it explicitly.
-    if (topo_prefix == linearization.size()) {
-        assert(linearization == linearization_fixed);
-    }
-}
```

### src/txgraph.cpp
```diff
@@ -40,10 +40,12 @@ enum class QualityLevel
     /** This is a singleton cluster consisting of a transaction that individually exceeds the
      *  cluster size limit. It cannot be merged with anything. */
     OVERSIZED_SINGLETON,
+    /** This cluster may have multiple disconnected components, which are all NEEDS_FIX. */
+    NEEDS_SPLIT_FIX,
     /** This cluster may have multiple disconnected components, which are all NEEDS_RELINEARIZE. */
     NEEDS_SPLIT,
-    /** This cluster may have multiple disconnected components, which are all ACCEPTABLE. */
-    NEEDS_SPLIT_ACCEPTABLE,
+    /** This cluster may be non-topological. */
+    NEEDS_FIX,
     /** This cluster has undergone changes that warrant re-linearization. */
     NEEDS_RELINEARIZE,
     /** The minimal level of linearization has been performed, but it is not known to be optimal. */
@@ -128,10 +130,14 @@ class Cluster
     // Generic helper functions.
 
     /** Whether the linearization of this Cluster can be exposed. */
-    bool IsAcceptable(bool after_split = false) const noexcept
+    bool IsAcceptable() const noexcept
     {
-        return m_quality == QualityLevel::ACCEPTABLE || m_quality == QualityLevel::OPTIMAL ||
-               (after_split && m_quality == QualityLevel::NEEDS_SPLIT_ACCEPTABLE);
+        return m_quality == QualityLevel::ACCEPTABLE || m_quality == QualityLevel::OPTIMAL;
+    }
+    /** Whether the linearization of this Cluster is topological. */
+    bool IsTopological() const noexcept
+    {
+        return m_quality != QualityLevel::NEEDS_FIX && m_quality != QualityLevel::NEEDS_SPLIT_FIX;
     }
     /** Whether the linearization of this Cluster is optimal. */
     bool IsOptimal() const noexcept
@@ -145,8 +151,7 @@ class Cluster
     /** Whether this cluster requires splitting. */
     bool NeedsSplitting() const noexcept
     {
-        return m_quality == QualityLevel::NEEDS_SPLIT ||
-               m_quality == QualityLevel::NEEDS_SPLIT_ACCEPTABLE;
+        return m_quality == QualityLevel::NEEDS_SPLIT || m_quality == QualityLevel::NEEDS_SPLIT_FIX;
     }
 
     /** Get the smallest number of transactions this Cluster is intended for. */
@@ -169,8 +174,9 @@ class Cluster
     virtual DepGraphIndex AppendTransaction(GraphIndex graph_idx, FeePerWeight feerate) noexcept = 0;
     /** Add dependencies to a given child in this cluster. */
     virtual void AddDependencies(SetType parents, DepGraphIndex child) noexcept = 0;
-    /** Invoke visitor_fn for each transaction in the cluster, in linearization order, then wipe this Cluster. */
-    virtual void ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight, SetType)>& visit_fn) noexcept = 0;
+    /** Invoke visit1_fn for each transaction in the cluster, in linearization order, then
+     *  visit2_fn in the same order, then wipe this Cluster. */
+    virtual void ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight)>& visit1_fn, const std::function<void (DepGraphIndex, GraphIndex, SetType)>& visit2_fn) noexcept = 0;
     /** Figure out what level this Cluster exists at in the graph. In most cases this is known by
      *  the caller already (see all "int level" arguments below), but not always. */
     virtual int GetLevel(const TxGraphImpl& graph) const noexcept = 0;
@@ -270,7 +276,7 @@ class GenericClusterImpl final : public Cluster
     GraphIndex GetClusterEntry(DepGraphIndex index) const noexcept final { return m_mapping[index]; }
     DepGraphIndex AppendTransaction(GraphIndex graph_idx, FeePerWeight feerate) noexcept final;
     void AddDependencies(SetType parents, DepGraphIndex child) noexcept final;
-    void ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight, SetType)>& visit_fn) noexcept final;
+    void ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight)>& visit1_fn, const std::function<void (DepGraphIndex, GraphIndex, SetType)>& visit2_fn) noexcept final;
     int GetLevel(const TxGraphImpl& graph) const noexcept final;
     void UpdateMapping(DepGraphIndex cluster_idx, GraphIndex graph_idx) noexcept final { m_mapping[cluster_idx] = graph_idx; }
     void Updated(TxGraphImpl& graph, int level) noexcept final;
@@ -326,7 +332,7 @@ class SingletonClusterImpl final : public Cluster
     GraphIndex GetClusterEntry(DepGraphIndex index) const noexcept final { Assume(index == 0); Assume(GetTxCount()); return m_graph_index; }
     DepGraphIndex AppendTransaction(GraphIndex graph_idx, FeePerWeight feerate) noexcept final;
     void AddDependencies(SetType parents, DepGraphIndex child) noexcept final;
-    void ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight, SetType)>& visit_fn) noexcept final;
+    void ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight)>& visit1_fn, const std::function<void (DepGraphIndex, GraphIndex, SetType)>& visit2_fn) noexcept final;
     int GetLevel(const TxGraphImpl& graph) const noexcept final;
     void UpdateMapping(DepGraphIndex cluster_idx, GraphIndex graph_idx) noexcept final { Assume(cluster_idx == 0); m_graph_index = graph_idx; }
     void Updated(TxGraphImpl& graph, int level) noexcept final;
@@ -917,21 +923,25 @@ void SingletonClusterImpl::AddDependencies(SetType parents, DepGraphIndex child)
     Assume(parents == SetType{} || parents == SetType::Fill(0));
 }
 
-void GenericClusterImpl::ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight, SetType)>& visit_fn) noexcept
+void GenericClusterImpl::ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight)>& visit1_fn, const std::function<void (DepGraphIndex, GraphIndex, SetType)>& visit2_fn) noexcept
 {
     for (auto pos : m_linearization) {
-        visit_fn(pos, m_mapping[pos], FeePerWeight::FromFeeFrac(m_depgraph.FeeRate(pos)), m_depgraph.GetReducedParents(pos));
+        visit1_fn(pos, m_mapping[pos], FeePerWeight::FromFeeFrac(m_depgraph.FeeRate(pos)));
+    }
+    for (auto pos : m_linearization) {
+        visit2_fn(pos, m_mapping[pos], m_depgraph.GetReducedParents(pos));
     }
     // Purge this Cluster, now that everything has been moved.
     m_depgraph = DepGraph<SetType>{};
     m_linearization.clear();
     m_mapping.clear();
 }
 
-void SingletonClusterImpl::ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight, SetType)>& visit_fn) noexcept
+void SingletonClusterImpl::ExtractTransactions(const std::function<void (DepGraphIndex, GraphIndex, FeePerWeight)>& visit1_fn, const std::function<void (DepGraphIndex, GraphIndex, SetType)>& visit2_fn) noexcept
 {
     if (GetTxCount()) {
-        visit_fn(0, m_graph_index, m_feerate, SetType{});
+        visit1_fn(0, m_graph_index, m_feerate);
+        visit2_fn(0, m_graph_index, SetType{});
         m_graph_index = NO_GRAPH_INDEX;
     }
 }
@@ -1179,37 +1189,21 @@ void GenericClusterImpl::ApplyRemovals(TxGraphImpl& graph, int level, std::span<
         to_remove = to_remove.subspan(1);
     } while(!to_remove.empty());
 
-    auto quality = m_quality;
     Assume(todo.Any());
     // Wipe from the Cluster's DepGraph (this is O(n) regardless of the number of entries
     // removed, so we benefit from batching all the removals).
     m_depgraph.RemoveTransactions(todo);
     m_mapping.resize(m_depgraph.PositionRange());
 
-    // First remove all removals at the end of the linearization.
-    while (!m_linearization.empty() && todo[m_linearization.back()]) {
-        todo.Reset(m_linearization.back());
-        m_linearization.pop_back();
-    }
-    if (todo.None()) {
-        // If no further removals remain, and thus all removals were at the end, we may be able
-        // to leave the cluster at a better quality level.
-        if (IsAcceptable(/*after_split=*/true)) {
-            quality = QualityLevel::NEEDS_SPLIT_ACCEPTABLE;
-        } else {
-            quality = QualityLevel::NEEDS_SPLIT;
-        }
-    } else {
-        // If more removals remain, filter those out of m_linearization.
-        m_linearization.erase(std::remove_if(
-            m_linearization.begin(),
-            m_linearization.end(),
-            [&](auto pos) { return todo[pos]; }), m_linearization.end());
-        quality = QualityLevel::NEEDS_SPLIT;
-    }
+    // Filter removed transactions out of m_linearization.
+    m_linearization.erase(std::remove_if(m_linearization.begin(), m_linearization.end(),
+                                         [&](auto pos) { return todo[pos]; }),
+                          m_linearization.end());
+
     Compact();
     graph.GetClusterSet(level).m_cluster_usage += TotalMemoryUsage();
-    graph.SetClusterQuality(level, m_quality, m_setindex, quality);
+    auto new_quality = IsTopological() ? QualityLevel::NEEDS_SPLIT : QualityLevel::NEEDS_SPLIT_FIX;
+    graph.SetClusterQuality(level, m_quality, m_setindex, new_quality);
     Updated(graph, level);
 }
 
@@ -1311,6 +1305,7 @@ void SingletonClusterImpl::AppendChunkFeerates(std::vector<FeeFrac>& ret) const
 
 uint64_t GenericClusterImpl::AppendTrimData(std::vector<TrimTxData>& ret, std::vector<std::pair<GraphIndex, GraphIndex>>& deps) const noexcept
 {
+    Assume(IsAcceptable());
     auto linchunking = ChunkLinearizationInfo(m_depgraph, m_linearization);
     LinearizationIndex pos{0};
     uint64_t size{0};
@@ -1354,17 +1349,7 @@ bool GenericClusterImpl::Split(TxGraphImpl& graph, int level) noexcept
     // This function can only be called when the Cluster needs splitting.
     Assume(NeedsSplitting());
     // Determine the new quality the split-off Clusters will have.
-    QualityLevel new_quality = IsAcceptable(/*after_split=*/true) ? QualityLevel::ACCEPTABLE
-                                                                  : QualityLevel::NEEDS_RELINEARIZE;
-    // If we're going to produce ACCEPTABLE clusters (i.e., when in NEEDS_SPLIT_ACCEPTABLE), we
-    // need to post-linearize to make sure the split-out versions are all connected (as
-    // connectivity may have changed by removing part of the cluster). This could be done on each
-    // resulting split-out cluster separately, but it is simpler to do it once up front before
-    // splitting. This step is not necessary if the resulting clusters are NEEDS_RELINEARIZE, as
-    // they will be post-linearized anyway in MakeAcceptable().
-    if (new_quality == QualityLevel::ACCEPTABLE) {
-        PostLinearize(m_depgraph, m_linearization);
-    }
+    QualityLevel new_quality = IsTopological() ? QualityLevel::NEEDS_RELINEARIZE : QualityLevel::NEEDS_FIX;
     /** Which positions are still left in this Cluster. */
     auto todo = m_depgraph.Positions();
     /** Mapping from transaction positions in this Cluster to the Cluster where it ends up, and
@@ -1376,7 +1361,7 @@ bool GenericClusterImpl::Split(TxGraphImpl& graph, int level) noexcept
     while (todo.Any()) {
         auto component = m_depgraph.FindConnectedComponent(todo);
         auto component_size = component.Count();
-        auto split_quality = component_size <= 2 ? QualityLevel::OPTIMAL : new_quality;
+        auto split_quality = component_size <= 1 ? QualityLevel::OPTIMAL : new_quality;
         if (first && component == todo && SetType::Fill(component_size) == component && component_size >= MIN_INTENDED_TX_COUNT) {
             // The existing Cluster is an entire component, without holes. Leave it be, but update
             // its quality. If there are holes, we continue, so that the Cluster is reconstructed
@@ -1446,7 +1431,7 @@ void GenericClusterImpl::Merge(TxGraphImpl& graph, int level, Cluster& other) no
     /** Vector to store the positions in this Cluster for each position in other. */
     std::vector<DepGraphIndex> remap(other.GetDepGraphIndexRange());
     // Iterate over all transactions in the other Cluster (the one being absorbed).
-    other.ExtractTransactions([&](DepGraphIndex pos, GraphIndex idx, FeePerWeight feerate, SetType other_parents) noexcept {
+    other.ExtractTransactions([&](DepGraphIndex pos, GraphIndex idx, FeePerWeight feerate) noexcept {
         // Copy the transaction into this Cluster, and remember its position.
         auto new_pos = m_depgraph.AddTransaction(feerate);
         // Since this cluster must have been made hole-free before being merged into, all added
@@ -1455,9 +1440,8 @@ void GenericClusterImpl::Merge(TxGraphImpl& graph, int level, Cluster& other) no
         remap[pos] = new_pos;
         m_mapping.push_back(idx);
         m_linearization.push_back(new_pos);
-        // Copy the transaction's dependencies, translating them using remap. Note that since
-        // pos iterates in linearization order, which is topological, all parents of pos should
-        // already be in remap.
+    }, [&](DepGraphIndex pos, GraphIndex idx, SetType other_parents) noexcept {
+        // Copy the transaction's dependencies, translating them using remap.
         SetType parents;
         for (auto par : other_parents) {
             parents.Set(remap[par]);
@@ -1470,7 +1454,7 @@ void GenericClusterImpl::Merge(TxGraphImpl& graph, int level, Cluster& other) no
         // Discard any potential ChunkData prior to modifying the Cluster (as that could
         // invalidate its ordering).
         if (level == 0) graph.ClearChunkData(entry);
-        entry.m_locator[level].SetPresent(this, new_pos);
+        entry.m_locator[level].SetPresent(this, remap[pos]);
     });
 }
 
@@ -1482,14 +1466,6 @@ void SingletonClusterImpl::Merge(TxGraphImpl&, int, Cluster&) noexcept
 
 void GenericClusterImpl::ApplyDependencies(TxGraphImpl& graph, int level, std::span<std::pair<GraphIndex, GraphIndex>> to_apply) noexcept
 {
-    // This function is invoked by TxGraphImpl::ApplyDependencies after merging groups of Clusters
-    // between which dependencies are added, which simply concatenates their linearizations. Invoke
-    // PostLinearize, which has the effect that the linearization becomes a merge-sort of the
-    // constituent linearizations. Do this here rather than in Cluster::Merge, because this
-    // function is only invoked once per merged Cluster, rather than once per constituent one.
-    // This concatenation + post-linearization could be replaced with an explicit merge-sort.
-    PostLinearize(m_depgraph, m_linearization);
-
     // Sort the list of dependencies to apply by child, so those can be applied in batch.
     std::sort(to_apply.begin(), to_apply.end(), [](auto& a, auto& b) { return a.second < b.second; });
     // Iterate over groups of to-be-added dependencies with the same child.
@@ -1514,15 +1490,11 @@ void GenericClusterImpl::ApplyDependencies(TxGraphImpl& graph, int level, std::s
         m_depgraph.AddDependencies(parents, child_idx);
     }
 
-    // Finally fix the linearization, as the new dependencies may have invalidated the
-    // linearization, and post-linearize it to fix up the worst problems with it.
-    FixLinearization(m_depgraph, m_linearization);
-    PostLinearize(m_depgraph, m_linearization);
+    // Finally set the cluster to NEEDS_FIX, so its linearization is fixed the next time it is
+    // attempted to be made ACCEPTABLE.
     Assume(!NeedsSplitting());
     Assume(!IsOversized());
-    if (IsAcceptable()) {
-        graph.SetClusterQuality(level, m_quality, m_setindex, QualityLevel::NEEDS_RELINEARIZE);
-    }
+    graph.SetClusterQuality(level, m_quality, m_setindex, QualityLevel::NEEDS_FIX);
 
     // Finally push the changes to graph.m_entries.
     Updated(graph, level);
@@ -1771,7 +1743,7 @@ void TxGraphImpl::SplitAll(int up_to_level) noexcept
     // Before splitting all Cluster, first make sure all removals are applied.
     ApplyRemovals(up_to_level);
     for (int level = 0; level <= up_to_level; ++level) {
-        for (auto quality : {QualityLevel::NEEDS_SPLIT, QualityLevel::NEEDS_SPLIT_ACCEPTABLE}) {
+        for (auto quality : {QualityLevel::NEEDS_SPLIT_FIX, QualityLevel::NEEDS_SPLIT}) {
             auto& queue = GetClusterSet(level).m_clusters[int(quality)];
             while (!queue.empty()) {
                 Split(*queue.back().get(), level);
@@ -2089,7 +2061,7 @@ std::pair<uint64_t, bool> GenericClusterImpl::Relinearize(TxGraphImpl& graph, in
     if (IsOptimal()) return {0, false};
     // Invoke the actual linearization algorithm (passing in the existing one).
     uint64_t rng_seed = graph.m_rng.rand64();
-    auto [linearization, optimal, cost] = Linearize(m_depgraph, max_iters, rng_seed, m_linearization);
+    auto [linearization, optimal, cost] = Linearize(m_depgraph, max_iters, rng_seed, m_linearization, /*is_topological=*/IsTopological());
     // Postlinearize to undo some of the non-determinism caused by randomizing the linearization.
     // This also guarantees that all chunks are connected (which is not guaranteed by SFL
     // currently, even when optimal).
@@ -2104,6 +2076,9 @@ std::pair<uint64_t, bool> GenericClusterImpl::Relinearize(TxGraphImpl& graph, in
     } else if (max_iters >= graph.m_acceptable_iters && !IsAcceptable()) {
         graph.SetClusterQuality(level, m_quality, m_setindex, QualityLevel::ACCEPTABLE);
         improved = true;
+    } else if (!IsTopological()) {
+        graph.SetClusterQuality(level, m_quality, m_setindex, QualityLevel::NEEDS_RELINEARIZE);
+        improved = true;
     }
     // Update the Entry objects.
     Updated(graph, level);
@@ -2131,9 +2106,11 @@ void TxGraphImpl::MakeAllAcceptable(int level) noexcept
     ApplyDependencies(level);
     auto& clusterset = GetClusterSet(level);
     if (clusterset.m_oversized == true) return;
-    auto& queue = clusterset.m_clusters[int(QualityLevel::NEEDS_RELINEARIZE)];
-    while (!queue.empty()) {
-        MakeAcceptable(*queue.back().get(), level);
+    for (auto quality : {QualityLevel::NEEDS_FIX, QualityLevel::NEEDS_RELINEARIZE}) {
+        auto& queue = clusterset.m_clusters[int(quality)];
+        while (!queue.empty()) {
+            MakeAcceptable(*queue.back().get(), level);
+        }
     }
 }
 
@@ -2640,10 +2617,8 @@ void GenericClusterImpl::SetFee(TxGraphImpl& graph, int level, DepGraphIndex idx
     m_depgraph.FeeRate(idx).fee = fee;
     if (m_quality == QualityLevel::OVERSIZED_SINGLETON) {
         // Nothing to do.
-    } else if (!NeedsSplitting()) {
+    } else if (IsAcceptable()) {
         graph.SetClusterQuality(level, m_quality, m_setindex, QualityLevel::NEEDS_RELINEARIZE);
-    } else {
-        graph.SetClusterQuality(level, m_quality, m_setindex, QualityLevel::NEEDS_SPLIT);
     }
     Updated(graph, level);
 }
@@ -2771,7 +2746,9 @@ void GenericClusterImpl::SanityCheck(const TxGraphImpl& graph, int level) const
         const auto& entry = graph.m_entries[m_mapping[lin_pos]];
         // Check that the linearization is topological.
         m_done.Set(lin_pos);
-        assert(m_done.IsSupersetOf(m_depgraph.Ancestors(lin_pos)));
+        if (IsTopological()) {
+            assert(m_done.IsSupersetOf(m_depgraph.Ancestors(lin_pos)));
+        }
         // Check that the Entry has a locator pointing back to this Cluster & position within it.
         assert(entry.m_locator[level].cluster == this);
         assert(entry.m_locator[level].index == lin_pos);
@@ -3010,7 +2987,7 @@ bool TxGraphImpl::DoWork(uint64_t iters) noexcept
     uint64_t iters_done{0};
     // First linearize everything in NEEDS_RELINEARIZE to an acceptable level. If more budget
     // remains after that, try to make everything optimal.
-    for (QualityLevel quality : {QualityLevel::NEEDS_RELINEARIZE, QualityLevel::ACCEPTABLE}) {
+    for (QualityLevel quality : {QualityLevel::NEEDS_FIX, QualityLevel::NEEDS_RELINEARIZE, QualityLevel::ACCEPTABLE}) {
         // First linearize staging, if it exists, then main.
         for (int level = GetTopLevel(); level >= 0; --level) {
             // Do not modify main if it has any observers.
@@ -3027,7 +3004,7 @@ bool TxGraphImpl::DoWork(uint64_t iters) noexcept
                 // one.
                 auto pos = m_rng.randrange<size_t>(queue.size());
                 auto iters_now = iters - iters_done;
-                if (quality == QualityLevel::NEEDS_RELINEARIZE) {
+                if (quality == QualityLevel::NEEDS_FIX || quality == QualityLevel::NEEDS_RELINEARIZE) {
                     // If we're working with clusters that need relinearization still, only perform
                     // up to m_acceptable_iters iterations. If they become ACCEPTABLE, and we still
                     // have budget after all other clusters are ACCEPTABLE too, we'll spend the
@@ -3289,6 +3266,7 @@ std::vector<TxGraph::Ref*> TxGraphImpl::Trim() noexcept
                                 .subspan(group_data.m_cluster_offset, group_data.m_cluster_count);
         uint64_t size{0};
         for (Cluster* cluster : cluster_span) {
+            MakeAcceptable(*cluster, cluster->GetLevel(*this));
             size += cluster->AppendTrimData(trim_data, deps_by_child);
         }
         // If this group of Clusters does not violate any limits, continue to the next group.
```
