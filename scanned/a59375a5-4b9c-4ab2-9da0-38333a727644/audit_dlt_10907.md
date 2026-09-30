# [?] SC-811 Estimator overflow fix

## Summary
Severity: Unknown
Chain: Waves
Component: wavesplatform/Waves
Published: 2021-11-30
Source: https://github.com/wavesplatform/Waves/commit/299501dc1ac02989fa996e2b153af2e7e0f154b3
Type: security-commit

## Details
SC-811 Estimator overflow fix

## Patch
### grpc-server/src/test/scala/com/wavesplatform/events/BlockchainUpdatesSpec.scala
```diff
@@ -497,7 +497,7 @@ class BlockchainUpdatesSpec extends FreeSpec with WithDomain with ScalaFutures w
            |  ]
            |}
            |""".stripMargin,
-          ScriptEstimatorV3
+          ScriptEstimatorV3(fixOverflow = true)
         )
         .explicitGet()
       val invoke = InvokeScriptTransaction
```

### lang/js/src/main/scala/JsAPI.scala
```diff
@@ -44,6 +44,8 @@ object JsAPI {
   private def buildContractContext(v: StdLibVersion): CTX[Environment] =
     Monoid.combineAll(Seq(pureContext(v), cryptoContext(v), wavesContext(v, false, true)))
 
+  private val allEstimators: Seq[ScriptEstimator] = ScriptEstimator.all(fixOverflow = true)
+
   @JSExportTopLevel("getTypes")
   def getTypes(ver: Int = 2, isTokenContext: Boolean = false, isContract: Boolean = false): js.Array[js.Object with js.Dynamic] =
     buildScriptContext(DirectiveDictionary[StdLibVersion].idMap(ver), isTokenContext, isContract).types
@@ -128,14 +130,14 @@ object JsAPI {
   ): js.Dynamic = {
     val r = for {
       estimatorVer <- Either.cond(
-        estimatorVersion > 0 && estimatorVersion <= ScriptEstimator.all.length,
+        estimatorVersion > 0 && estimatorVersion <= allEstimators.length,
         estimatorVersion,
-        s"Version of estimator must be not greater than ${ScriptEstimator.all.length}"
+        s"Version of estimator must be not greater than ${allEstimators.length}"
       )
       directives  <- DirectiveParser(input)
       ds          <- extractDirectives(directives)
       linkedInput <- ScriptPreprocessor(input, libraries.toMap, ds.imports)
-      compiled    <- parseAndCompileScript(ds, linkedInput, ScriptEstimator.all.toIndexedSeq(estimatorVer - 1), needCompaction, removeUnusedCode)
+      compiled    <- parseAndCompileScript(ds, linkedInput, allEstimators.toIndexedSeq(estimatorVer - 1), needCompaction, removeUnusedCode)
     } yield compiled
     r.fold(
       e => js.Dynamic.literal("error" -> e),
@@ -204,14 +206,14 @@ object JsAPI {
   ): js.Dynamic = {
     val r = for {
       estimatorVer <- Either.cond(
-        estimatorVersion > 0 && estimatorVersion <= ScriptEstimator.all.length,
+        estimatorVersion > 0 && estimatorVersion <= allEstimators.length,
         estimatorVersion,
-        s"Version of estimator must be not greater than ${ScriptEstimator.all.length}"
+        s"Version of estimator must be not greater than ${allEstimators.length}"
       )
       directives  <- DirectiveParser(input)
       ds          <- extractDirectives(directives)
       linkedInput <- ScriptPreprocessor(input, libraries.toMap, ds.imports)
-      compiled    <- compileScript(ds, linkedInput, ScriptEstimator.all.toIndexedSeq(estimatorVer - 1), needCompaction, removeUnusedCode)
+      compiled    <- compileScript(ds, linkedInput, allEstimators.toIndexedSeq(estimatorVer - 1), needCompaction, removeUnusedCode)
     } yield compiled
     r.fold(
       e => js.Dynamic.literal("error" -> e),
```

### lang/shared/src/main/scala/com/wavesplatform/lang/v1/estimator/ScriptEstimator.scala
```diff
@@ -17,6 +17,6 @@ trait ScriptEstimator {
 }
 
 object ScriptEstimator {
-  val all: List[ScriptEstimator] =
-    List(ScriptEstimatorV1, ScriptEstimatorV2, ScriptEstimatorV3)
-}
\ No newline at end of file
+  def all(fixOverflow: Boolean): List[ScriptEstimator] =
+    List(ScriptEstimatorV1, ScriptEstimatorV2, ScriptEstimatorV3(fixOverflow))
+}
```

### lang/shared/src/main/scala/com/wavesplatform/lang/v1/estimator/v3/ScriptEstimatorV3.scala
```diff
@@ -1,7 +1,6 @@
 package com.wavesplatform.lang.v1.estimator.v3
 
-import cats.instances.list._
-import cats.syntax.traverse._
+import cats.implicits._
 import cats.{Id, Monad}
 import com.wavesplatform.lang.ExecutionError
 import com.wavesplatform.lang.v1.FunctionHeader
@@ -12,7 +11,9 @@ import com.wavesplatform.lang.v1.estimator.v3.EstimatorContext.Lenses._
 import com.wavesplatform.lang.v1.task.imports._
 import monix.eval.Coeval
 
-object ScriptEstimatorV3 extends ScriptEstimator {
+import scala.util.Try
+
+case class ScriptEstimatorV3(fixOverflow: Boolean) extends ScriptEstimator {
   override val version: Int = 3
 
   override def apply(
@@ -58,7 +59,8 @@ object ScriptEstimatorV3 extends ScriptEstimator {
       ctx      <- get[Id, EstimatorContext, ExecutionError]
       letCost  <- if (ctx.usedRefs.contains(let.name)) letEval else const(0L)
       _        <- update(usedRefs.modify(_)(r => if (overlap) r + let.name else r - let.name))
-    } yield nextCost + letCost
+      result   <- sum(nextCost, letCost)
+    } yield result
 
   private def evalFuncBlock(func: FUNC, inner: EXPR): EvalM[Long] =
     for {
@@ -83,13 +85,15 @@ object ScriptEstimatorV3 extends ScriptEstimator {
       cond  <- evalHoldingFuncs(cond)
       right <- evalHoldingFuncs(ifTrue)
       left  <- evalHoldingFuncs(ifFalse)
-    } yield cond + Math.max(right, left) + 1
+      r1    <- sum(cond, Math.max(right, left))
+      r2    <- sum(r1, 1)
+    } yield r2
 
   private def markRef(key: String): EvalM[Long] =
     update(usedRefs.modify(_)(_ + key)).map(_ => 1)
 
   private def evalGetter(expr: EXPR): EvalM[Long] =
-    evalExpr(expr).map(_ + 1)
+    evalExpr(expr).flatMap(sum(_, 1))
 
   private def evalFuncCall(header: FunctionHeader, args: List[EXPR]): EvalM[Long] =
     for {
@@ -108,12 +112,19 @@ object ScriptEstimatorV3 extends ScriptEstimator {
             )
         }
       )
-      argsCost <- args.traverse(evalHoldingFuncs)
-    } yield argsCost.sum + bodyCost.value()
+      argsCosts    <- args.traverse(evalHoldingFuncs)
+      argsCostsSum <- argsCosts.foldM(0L)(sum)
+      result       <- sum(argsCostsSum, bodyCost.value())
+    } yield result
 
   private def update(f: EstimatorContext => EstimatorContext): EvalM[Unit] =
     modify[Id, EstimatorContext, ExecutionError](f)
 
   private def const[A](a: A): EvalM[A] =
     Monad[EvalM].pure(a)
+
+  private def sum(a: Long, b: Long): EvalM[Long] = {
+    def r = if (fixOverflow) Math.addExact(a, b) else a + b
+    liftEither(Try(r).toEither.leftMap(_ => "Illegal script"))
+  }
 }
```

### lang/shared/src/main/scala/com/wavesplatform/lang/v1/evaluator/ContractEvaluator.scala
```diff
@@ -90,8 +90,7 @@ object ContractEvaluator {
   def verify(
       decls: List[DECLARATION],
       v: VerifierFunction,
-      ctx: EvaluationContext[Environment, Id],
-      evaluate: (EvaluationContext[Environment, Id], EXPR) => (Log[Id], Int, Either[ExecutionError, EVALUATED]),
+      evaluate: EXPR => (Log[Id], Int, Either[ExecutionError, EVALUATED]),
       entity: CaseObj
   ): (Log[Id], Int, Either[ExecutionError, EVALUATED]) = {
     val verifierBlock =
@@ -100,7 +99,7 @@ object ContractEvaluator {
         BLOCK(v.u, FUNCTION_CALL(FunctionHeader.User(v.u.name), List(entity)))
       )
 
-    evaluate(ctx, foldDeclarations(decls, verifierBlock))
+    evaluate(foldDeclarations(decls, verifierBlock))
   }
 
   def applyV2Coeval(
```

### lang/tests/src/test/scala/com/wavesplatform/lang/ContractIntegrationTest.scala
```diff
@@ -182,8 +182,7 @@ class ContractIntegrationTest extends PropSpec with Inside {
     ContractEvaluator.verify(
       compiled.decs,
       compiled.verifierFuncOpt.get,
-      ctx.evaluationContext(environment),
-      EvaluatorV2.applyCompleted(_, _, V3),
+      EvaluatorV2.applyCompleted(ctx.evaluationContext(environment), _, V3),
       txObject
     )._3
   }
```

### lang/tests/src/test/scala/com/wavesplatform/lang/compiler/ContractCompilerTest.scala
```diff
@@ -1008,7 +1008,7 @@ class ContractCompilerTest extends PropSpec {
         |
       """.stripMargin
 
-    Global.compileContract(dApp, dAppV4Ctx, V4, ScriptEstimatorV3, false, false) should produce("Script is too large: 37551 bytes > 32768 bytes")
+    Global.compileContract(dApp, dAppV4Ctx, V4, ScriptEstimatorV3(fixOverflow = true), false, false) should produce("Script is too large: 37551 bytes > 32768 bytes")
   }
 
   property("@Callable Invoke") {
```

### lang/tests/src/test/scala/com/wavesplatform/lang/compiler/ExpressionCompilerV1Test.scala
```diff
@@ -316,7 +316,7 @@ class ExpressionCompilerV1Test extends PropSpec {
       )
       .compilerContext
 
-    Global.compileExpression(expr, ctx, V4, ScriptEstimatorV3) should produce("Script is too large: 8756 bytes > 8192 bytes")
+    Global.compileExpression(expr, ctx, V4, ScriptEstimatorV3(fixOverflow = true)) should produce("Script is too large: 8756 bytes > 8192 bytes")
   }
 
   property("extract() removed from V4") {
```

### lang/tests/src/test/scala/com/wavesplatform/lang/v1/estimator/CommonScriptEstimatorTest.scala
```diff
@@ -8,7 +8,14 @@ import com.wavesplatform.lang.v1.estimator.v2.ScriptEstimatorV2
 import com.wavesplatform.lang.v1.estimator.v3.ScriptEstimatorV3
 import com.wavesplatform.lang.v1.evaluator.FunctionIds.SUM_LONG
 
-class CommonScriptEstimatorTest extends ScriptEstimatorTestBase(ScriptEstimatorV1, ScriptEstimatorV2, ScriptEstimatorV3, evaluatorV2AsEstimator) {
+class CommonScriptEstimatorTest
+    extends ScriptEstimatorTestBase(
+      ScriptEstimatorV1,
+      ScriptEstimatorV2,
+      ScriptEstimatorV3(fixOverflow = true),
+      ScriptEstimatorV3(fixOverflow = false),
+      evaluatorV2AsEstimator
+    ) {
   property("context leak") {
     def script(ref: String) =
       compile {
```

### lang/tests/src/test/scala/com/wavesplatform/lang/v1/estimator/FunctionComplexityTest.scala
```diff
@@ -43,7 +43,7 @@ class FunctionComplexityTest extends PropSpec {
         .filterNot(_.name.startsWith("_"))
         .foreach { function =>
           val expr = FUNCTION_CALL(function.header, List.fill(function.args.size)(Terms.TRUE))
-          val estimatedCost = ScriptEstimatorV3(
+          val estimatedCost = ScriptEstimatorV3(fixOverflow = true)(
             varNames(ds.stdLibVersion, ds.contentType),
             functionCosts(ds.stdLibVersion, ds.contentType),
             expr
```

### lang/tests/src/test/scala/com/wavesplatform/lang/v1/estimator/RecursiveFunctionTest.scala
```diff
@@ -8,7 +8,13 @@ import com.wavesplatform.lang.v1.compiler.Terms.{BLOCK, FUNC, FUNCTION_CALL}
 import com.wavesplatform.lang.v1.estimator.v2.ScriptEstimatorV2
 import com.wavesplatform.lang.v1.estimator.v3.ScriptEstimatorV3
 
-class RecursiveFunctionTest extends ScriptEstimatorTestBase(ScriptEstimatorV1, ScriptEstimatorV2, ScriptEstimatorV3) {
+class RecursiveFunctionTest
+    extends ScriptEstimatorTestBase(
+      ScriptEstimatorV1,
+      ScriptEstimatorV2,
+      ScriptEstimatorV3(fixOverflow = true),
+      ScriptEstimatorV3(fixOverflow = false)
+    ) {
   property("recursive func block") {
     val expr = BLOCK(
       FUNC("x", List.empty, FUNCTION_CALL(FunctionHeader.User("y"), List.empty)),
```

### lang/tests/src/test/scala/com/wavesplatform/lang/v1/estimator/ScriptEstimatorV2V3Test.scala
```diff
@@ -4,7 +4,12 @@ import com.wavesplatform.lang.v1.compiler.Terms.EXPR
 import com.wavesplatform.lang.v1.estimator.v2.ScriptEstimatorV2
 import com.wavesplatform.lang.v1.estimator.v3.ScriptEstimatorV3
 
-class ScriptEstimatorV2V3Test extends ScriptEstimatorTestBase(ScriptEstimatorV2, ScriptEstimatorV3) {
+class ScriptEstimatorV2V3Test
+    extends ScriptEstimatorTestBase(
+      ScriptEstimatorV2,
+      ScriptEstimatorV3(fixOverflow = true),
+      ScriptEstimatorV3(fixOverflow = false)
+    ) {
   property("transitive ref usage") {
     def refUsage(ref: String): EXPR =
       compile(
```
