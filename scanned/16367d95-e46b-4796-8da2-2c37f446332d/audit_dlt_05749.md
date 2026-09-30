# [?] [paper] Resolving supposed unsoundness issue around aborts behavioral predicate (#19584)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-04-29
Source: https://github.com/aptos-labs/aptos-core/commit/6a2e4207d1d4ec59686694f2008c662be268cb04
Type: security-commit

## Details
[paper] Resolving supposed unsoundness issue around aborts behavioral predicate (#19584)

It turns out this is a false positive since we can assume the function has verified successfully.

Also updated related work with insights about F* and Dafny.

## Patch
### aptos-move/framework/aptos-framework/doc/transaction_validation.md
```diff
@@ -65,6 +65,8 @@
     -  [Function `unified_prologue_v2`](#@Specification_1_unified_prologue_v2)
     -  [Function `unified_prologue_fee_payer_v2`](#@Specification_1_unified_prologue_fee_payer_v2)
     -  [Function `unified_epilogue_v2`](#@Specification_1_unified_epilogue_v2)
+    -  [Function `versioned_prologue`](#@Specification_1_versioned_prologue)
+    -  [Function `versioned_epilogue`](#@Specification_1_versioned_epilogue)
 
 
 <pre><code><b>use</b> <a href="account.md#0x1_account">0x1::account</a>;
@@ -2488,6 +2490,38 @@ Skip transaction_fee::burn_fee verification.
 
 
 
+<pre><code><b>pragma</b> verify = <b>false</b>;
+</code></pre>
+
+
+
+<a id="@Specification_1_versioned_prologue"></a>
+
+### Function `versioned_prologue`
+
+
+<pre><code><b>fun</b> <a href="transaction_validation.md#0x1_transaction_validation_versioned_prologue">versioned_prologue</a>(sender: <a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>, fee_payer: <a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>, args: <a href="transaction_validation.md#0x1_transaction_validation_PrologueArgs">transaction_validation::PrologueArgs</a>)
+</code></pre>
+
+
+
+
+<pre><code><b>pragma</b> verify = <b>false</b>;
+</code></pre>
+
+
+
+<a id="@Specification_1_versioned_epilogue"></a>
+
+### Function `versioned_epilogue`
+
+
+<pre><code><b>fun</b> <a href="transaction_validation.md#0x1_transaction_validation_versioned_epilogue">versioned_epilogue</a>(<a href="account.md#0x1_account">account</a>: <a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>, fee_payer: <a href="../../aptos-stdlib/../move-stdlib/doc/signer.md#0x1_signer">signer</a>, args: <a href="transaction_validation.md#0x1_transaction_validation_EpilogueArgs">transaction_validation::EpilogueArgs</a>)
+</code></pre>
+
+
+
+
 <pre><code><b>pragma</b> verify = <b>false</b>;
 </code></pre>
 
```

### third_party/move/move-prover/doc/higher-order-paper-26/conclusion.tex
```diff
@@ -10,11 +10,12 @@
 
 \fstar~\cite{fstar2016} likewise verifies higher-order, effectful code, internalizing the WP calculus in its type system via Dijkstra monads~\cite{dm4all}.
 Both systems support pre/post specifications, quantifiers, behavioral abstraction over function values, and structured proof guidance --- in Move via \texttt{proof} blocks, \texttt{lemma} declarations, and \texttt{calc}, \texttt{split}, \texttt{apply} statements.
-\fstar's dependent type and effect system goes beyond Move's support, which is more minimal and focused on Rust-style references and effects on global memory.
-Move also favors separation of specification from program code, which is useful in environments where work itself is distributed along that axis (for example, a multi-agent system).
+One major difference is that \fstar~is based on separation logic, while Move uses traditional frame conditions via modifies declarations. While \fstar~is more expressive via separation logic, it misses the syntactic, compile time separation of memory via Move's resource and reference model, potentially leading to significant more complex verification problems, as memory separation has to be reasoned about by the SMT solver.
 
-Dafny~\cite{DAFNY} is the closest cousin of \MVP: it has a similar specification model of pre/post conditions, higher-order functions, and behavioral predicates.
-Differences lie in the treatment of state: Move's resource-separated global memory and alias-free mutable reference model versus Dafny's heap model.
+Dafny~\cite{DAFNY} is a close cousin of \MVP: it has a similar specification model of pre/post conditions, higher-order functions, and behavioral predicates.
+However, Dafny does not allow function values to modify state.
+This would be a severe restriction for Move, since it is a common usage pattern.
+Moreover, Move's resource-separated global memory and alias-free mutable reference model is not available in Dafny, similar as in \fstar.
 While both languages support state labels, Move state labels as described here can be used in abstract specifications via universal and existential quantification.
 
 Lean~4~\cite{lean4} is a dependently-typed interactive theorem prover in the tradition of older similar systems~\cite{Isabelle, COQ}, supporting higher-order functions.
```

### third_party/move/move-prover/doc/higher-order-paper-26/encoding.tex
```diff
@@ -31,6 +31,7 @@
 The representation is further narrowed if the function value of a given type is not stored in a structure which ends in global memory.
 Storing a function value amounts to dynamic dispatch (think of building a 'vtable' explicitly), and this additional complexity is reflected by the $n$ in $F_{S.x}(n)$. Nevertheless, we are able to pinpoint a specification to $F_{S.x}(n)$, as has been seen for the AMM example (cf. Sec.~\ref{sec:amm}).
 
+
 \SubSection{Invoking Function Values}
 \label{sec:enc-invoke}
 
@@ -187,7 +188,7 @@
 \end{MoveBox}
 % @formatter:on
 
-\noindent As outlined in the last section, we want to be able to extract behavioral predicate functions from this specification.
+As outlined in the last section, we want to be able to extract behavioral predicate functions from this specification.
 For the ensures we can come up with the following, which simply replicates part of the spec:
 
 \begin{ivl}
@@ -197,10 +198,8 @@
         ensures_{\tau'}(g,\Mem^S,\Mem,a)\>
 \end{ivl}
 
-\noindent However, for the aborts which happens at the intermediate state !S! the situation is not that straightforward.
-The state !S! needs to be first established before the aborts condition can be checked for !g!.
-To achieve this, one could take all ensures conditions which reach !S! and then evaluate the aborts condition, as in:
-
+For the aborts which happens at the intermediate state !S!, the state !S! needs to be first established before the aborts condition can be checked for !g!.
+To achieve this, all ensures conditions which reach !S! are combined with the aborts condition, as in:
 
 \begin{ivl}
   \FUN aborts_{C_foo}[\Mem', \Mem](a) \\
@@ -209,29 +208,44 @@
         aborts_{\tau'}(g,\Mem^S,a)\>
 \end{ivl}
 
-\noindent But this is \emph{not} correct. To see this, consider that $f$ leaves the resource in a state such that $R[\Mem^S][a].0 > 0$ does not hold.
-In this case, the $aborts_{C_foo}$ above returns false, indicating that $foo$ would not abort.
-Yet it may very well abort if $g$ aborts in $\Mem^S$.
+This is semantically sound because we can assume inductively that the function $foo$ has successfully verified. For a successfully verified function, where $\sq{A}$ are the |aborts_if| conditions and $\sq{P}$ the |ensures| conditions, it holds:
+$$
+   \bigvee \sq{A} \lor \bigwedge \sq{P}
+$$
 
-The problem here is to differentiate between conditions which \emph{define} and which \emph{constrain} intermediate states.
-The current implementation in \MVP employs a heuristic to determine this:
+\noindent That is, either the function aborts under one of the given conditions, or all of its ensures conditions hold.
 
-\begin{itemize}
-\item Two-state behavioral predicates (!ensures_of! and !result_of!) are considered defining predicates.
-Also, a set of builtin predicates for publishing, updating, and removing resources are in this category.
-\item Everything else is considered a constraining predicate.
-\end{itemize}
+In general, since the relation between state labels spawn by predicates !S1..S2 |~ p! must be acyclic, one can extract from $\sq{P}$ those conditions which lead into $\Mem^S$, and from $\sq{A}$ those which start from state $\Mem^S$. Given this, the aborts condition can be synthesized using the following scheme:
+$$
+    \bigwedge \sq{P}_{..\Mem^S} \land (\bigvee \sq{A}_{\Mem^S} \lor
+    \bigwedge \sq{P}_{\Mem^S..\Mem^T} \land (\bigvee \sq{A}_{\Mem^T} \lor
+    \bigwedge \ldots ))
+$$
 
-\noindent In order to extract the condition for an aborts, \MVP will extract all conjuncts in the spec defining the state which reaches the aborts condition, stripping out conditions which are only constraining.
-This defining fragment of the spec is then combined with the aborts predicate.
-Practically, for the example above, we get:
+\noindent Here, $\sq{P}_{..\Mem^S}$ establish state $\Mem^S$ in which we check for the aborts condition $\sq{A}_{\Mem^S}$,
+or recurse over the remaining $\sq{P}$ and $\sq{A}$.
 
-\begin{ivl}
-  \FUN aborts_{C_{foo}}[\Mem', \Mem](a) \\
-\t1  \exists \Mem^S @
-      \<ensures_\tau(f,\Mem',\Mem^S,a) \land aborts_{\tau'}(g,\Mem^S,a)\>
-\end{ivl}
+\SubSection{Implementation Notes}
+
+Besides the conceptual description in this section, the implementation diverges from the idealized presentation in a few high-level ways for better SMT solving performance and cleaner Boogie output:
 
-We point out that the heuristic used here is potentially unsound.
-If $aborts_{C_{foo}}$ underapproximates and returns false where it should not, valid aborts scenarios can be missed in verification.
-This is a problem which requires future work and refinement.
+\begin{itemize}
+    \item \emph{Constraining state-label conjuncts are dropped from the existential.}
+    The paper's BP for an !aborts_if! at an intermediate state $\Mem^S$ includes \emph{all} ensures-with-$S$ conjuncts that reach $\Mem^S$ (including constraining ones such as $R[\Mem^S][a].0 > 0$).
+    The implementation restricts the existential body to the \emph{defining} conjuncts (those introducing label-defining operations like $\ensuresof{f}{\bar{x}}$, $\resultof{f}{\bar{x}}$, or the publish/remove/update builtins).
+    By the validity invariant $\bigvee \sq{A} \lor \bigwedge \sq{P}$, the constraining conjuncts hold at the witness chosen by foo's verification, so dropping them is sound for the BP.
+    Including them would only enlarge the formula without adding information.
+
+    \item \emph{Behavioral predicates are uninterpreted functions connected by axioms, not Boogie functions with explicit bodies.}
+    The paper writes $ensures_\tau$ as $\FUN \ldots = \mathit{body}$.
+    The implementation declares $ensures_\tau$ as an uninterpreted Boogie function and connects it to the per-function spec via an axiom of the form $(\forall\, \ldots\; ::\;  \mathit{eval\_call} \iff \mathit{rhs})$ with an explicit trigger pattern.
+    A Boogie \texttt{function \{body\}} is unfolded eagerly, so any quantifier in the body (typical for arithmetic identities or the prelude's vector axioms) spawns triggers at every call site, exploding the SMT search.
+    Axioms with explicit triggers fire only when the trigger pattern matches a ground term in the proof context, keeping instantiation under control.
+
+    \item \emph{Per-variant trigger specialization.}
+    The three variant kinds receive structurally different axioms: closure variants are triggered by the constructor application $C_f(c_0, \ldots, c_K)$ with capture variables bound by the quantifier, function-parameter variants are triggered by the nullary constructor $P_{f,x}()$, and struct-field variants are triggered by the evaluator itself with the variant pinned via an $f \IS F_{S.x}$ guard (because field values at call sites are typically opaque datatype values loaded from memory, not literal constructors).
+
+    \item \emph{State-label existential is flat, not recursive.}
+    The recursive scheme above is logically equivalent to a single flat $(\exists\, \Mem^S, \Mem^T, \ldots\; ::\;  \ldots)$ wrapping the conjunction of defining fragments and the kind-specific clauses.
+    The implementation uses the flat form, keeping the emitted Boogie smaller.
+\end{itemize}
```
