# [?] Allow limiting of witnesses in tree to prevent DoS attack during live editing

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-09-08
Source: https://github.com/penumbra-zone/penumbra/commit/14005a1d09a75ce7fec58e2c4f1fc8763f45e230
Type: security-commit

## Details
Allow limiting of witnesses in tree to prevent DoS attack during live editing

## Patch
### tct/examples/tct-live-edit.rs
```diff
@@ -19,6 +19,13 @@ struct Args {
     /// The port on which to serve the visualization and control API.
     #[clap(short, long, default_value = "8080")]
     port: u16,
+    /// The maximum number of commitments to permit witnessing before shedding them randomly.
+    ///
+    /// This is good to set if exposing this server to concurrent users, because it prevents a DoS
+    /// attack where someone keeps adding witnesses until the server runs out of memory and/or
+    /// clients fall over because they can't handle the size of the tree.
+    #[clap(long)]
+    max_witnesses: Option<usize>,
 }
 
 #[tokio::main]
@@ -36,7 +43,7 @@ async fn main() {
         ..Default::default()
     };
 
-    let app = live::edit(rng, tree, ext)
+    let app = live::edit(rng, tree, ext, args.max_witnesses)
         .merge(key_control())
         .layer(TraceLayer::new_for_http());
 
```

### tct/src/live.rs
```diff
@@ -25,9 +25,10 @@ pub fn edit<R: Rng + Send + 'static>(
     rng: R,
     tree: Arc<watch::Sender<Tree>>,
     ext: ViewExtensions,
+    max_commitments: Option<usize>,
 ) -> Router {
     // The three endpoints
-    let control = control(rng, tree.clone());
+    let control = control(rng, tree.clone(), max_commitments);
     let (query, mut changed) = query(tree.subscribe());
     let view = view(tree.subscribe(), ext);
 
```

### tct/src/live/control.rs
```diff
@@ -22,13 +22,17 @@ use crate::{
 /// Queries taking arguments pass arguments via URL parameters. Results are returned in JSON format,
 /// with [`StatusCode::BAD_REQUEST`] being returned if the operation failed (i.e. an `Err` variant
 /// was returned).
-pub fn control<R: Rng + Send + 'static>(rng: R, tree: Arc<watch::Sender<Tree>>) -> Router {
+pub fn control<R: Rng + Send + 'static>(
+    rng: R,
+    tree: Arc<watch::Sender<Tree>>,
+    max_witnesses: Option<usize>,
+) -> Router {
     // The rng is shared between all methods
     let rng = Arc::new(Mutex::new(rng));
 
     Router::new()
         .route("/new", new(tree.clone()))
-        .route("/insert", insert(rng.clone(), tree.clone()))
+        .route("/insert", insert(rng.clone(), tree.clone(), max_witnesses))
         .route("/forget", forget(rng.clone(), tree.clone()))
         .route(
             "/insert-block-root",
@@ -50,6 +54,7 @@ fn new(tree: Arc<watch::Sender<Tree>>) -> MethodRouter {
 fn insert<R: Rng + Send + 'static>(
     rng: Arc<Mutex<R>>,
     tree: Arc<watch::Sender<Tree>>,
+    max_witnesses: Option<usize>,
 ) -> MethodRouter {
     #[derive(Deserialize)]
     struct Insert {
@@ -58,12 +63,26 @@ fn insert<R: Rng + Send + 'static>(
     }
 
     post(
-        |Query(Insert {
-             witness,
-             commitment,
-         }): Query<Insert>| async move {
+        move |Query(Insert {
+                  witness,
+                  commitment,
+              }): Query<Insert>| async move {
             let mut result = None;
             tree.send_modify(|tree| {
+                if witness == Witness::Keep {
+                    // If we're at quota for number of commitments, forget until we're strictly below
+                    // quota again, so we can insert something
+                    if let Some(max_witnesses) = max_witnesses {
+                        let required_forgessions =
+                            (1 + tree.witnessed_count()).saturating_sub(max_witnesses);
+                        for commitment in
+                            random_commitments(&mut *rng.lock(), tree, required_forgessions)
+                        {
+                            tree.forget(commitment);
+                        }
+                    }
+                }
+                // Now actually insert the commitment we wanted to insert
                 result = Some(tree.insert(
                     witness,
                     // If no commitment is specified, generate a random one
@@ -85,6 +104,15 @@ fn insert<R: Rng + Send + 'static>(
     )
 }
 
+fn random_commitments<R: Rng>(mut rng: R, tree: &Tree, amount: usize) -> Vec<Commitment> {
+    tree.commitments()
+        .map(|(c, _)| c)
+        .collect::<Vec<_>>()
+        .choose_multiple(&mut rng, amount)
+        .copied()
+        .collect()
+}
+
 fn forget<R: Rng + Send + 'static>(
     rng: Arc<Mutex<R>>,
     tree: Arc<watch::Sender<Tree>>,
@@ -98,13 +126,8 @@ fn forget<R: Rng + Send + 'static>(
         let mut result = None;
         tree.send_modify(|tree| {
             if let Some(commitment) = commitment.or_else(|| {
-                // If no commitment is specified, forget a random one that is present in
-                // the tree
-                tree.commitments()
-                    .map(|(c, _)| c)
-                    .collect::<Vec<_>>()
-                    .choose(&mut *rng.lock())
-                    .copied()
+                // If no commitment is specified, forget a random extant one
+                random_commitments(&mut *rng.lock(), tree, 1).pop()
             }) {
                 result = Some(tree.forget(commitment));
             } else {
```
