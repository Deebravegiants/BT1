# [?] [refer #1033] Fix race condition in access IRContext in ErgoTransaction.validateStateful

## Summary
Severity: Unknown
Chain: Ergo
Component: ergoplatform/ergo
Published: 2020-01-17
Source: https://github.com/ergoplatform/ergo/commit/19f7d83354ccae4faa3125da99f8b06927a77262
Type: security-commit

## Details
[refer #1033] Fix race condition in access IRContext in ErgoTransaction.validateStateful

## Patch
### src/main/scala/org/ergoplatform/modifiers/mempool/ErgoTransaction.scala
```diff
@@ -121,102 +121,103 @@ case class ErgoTransaction(override val inputs: IndexedSeq[Input],
                        stateContext: ErgoStateContext,
                        accumulatedCost: Long)
                       (implicit verifier: ErgoInterpreter): ValidationState[Long] = {
-
-    verifier.IR.resetContext() // ensure there is no garbage in the IRContext
-    lazy val inputSumTry = Try(boxesToSpend.map(_.value).reduce(Math.addExact(_, _)))
-
-    // Cost of transaction initialization: we should read and parse all inputs and data inputs,
-    // and also iterate through all outputs to check rules
-    val initialCost: Long = addExact(
-      CostTable.interpreterInitCost,
-      multiplyExact(boxesToSpend.size, stateContext.currentParameters.inputCost),
-      multiplyExact(dataBoxes.size, stateContext.currentParameters.dataInputCost),
-      multiplyExact(outputCandidates.size, stateContext.currentParameters.outputCost),
-    )
-    val maxCost = stateContext.currentParameters.maxBlockCost
-
-    ModifierValidator(stateContext.validationSettings)
-      // Check that the transaction is not too big
-      .validate(bsBlockTransactionsCost, maxCost >= addExact(initialCost, accumulatedCost), s"$id: initial cost")
-      // Starting validation
-      .payload(initialCost)
-      // Perform cheap checks first
-      .validateNoFailure(txAssetsInOneBox, outAssetsTry)
-      .validate(txPositiveAssets, outputCandidates.forall(_.additionalTokens.forall(_._2 > 0)), s"$id: ${outputCandidates.map(_.additionalTokens)}")
-      // Check that outputs are not dust, and not created in future
-      .validateSeq(outputs) { case (validationState, out) =>
-      validationState
-        .validate(txDust, out.value >= BoxUtils.minimalErgoAmount(out, stateContext.currentParameters), s"$id, output ${Algos.encode(out.id)}, ${out.value} >= ${BoxUtils.minimalErgoAmount(out, stateContext.currentParameters)}")
-        .validate(txFuture, out.creationHeight <= stateContext.currentHeight, s"$id: output $out")
-        .validate(txBoxSize, out.bytes.length <= MaxBoxSize.value, s"$id: output $out")
-        .validate(txBoxPropositionSize, out.propositionBytes.length <= MaxPropositionBytes.value, s"$id: output $out")
-    }
-      // Just to be sure, check that all the input boxes to spend (and to read) are presented.
-      // Normally, this check should always pass, if the client is implemented properly
-      // so it is not part of the protocol really.
-      .validate(txBoxesToSpend, boxesToSpend.size == inputs.size, s"$id: ${boxesToSpend.size} == ${inputs.size}")
-      .validate(txDataBoxes, dataBoxes.size == dataInputs.size, s"$id: ${dataBoxes.size} == ${dataInputs.size}")
-      // Check that there are no overflow in input and output values
-      .validate(txInputsSum, inputSumTry.isSuccess, s"$id")
-      // Check that transaction is not creating money out of thin air.
-      .validate(txErgPreservation, inputSumTry == outputsSumTry, s"$id: $inputSumTry == $outputsSumTry")
-      .validateTry(outAssetsTry, e => ModifierValidator.fatal("Incorrect assets", e)) { case (validation, (outAssets, outAssetsNum)) =>
-        ErgoTransaction.extractAssets(boxesToSpend) match {
-          case Success((inAssets, inAssetsNum)) =>
-            lazy val newAssetId = ByteArrayWrapper(inputs.head.boxId)
-            val tokenAccessCost = stateContext.currentParameters.tokenAccessCost
-            val currentTxCost = validation.result.payload.get
-            // Cost of assets preservation rules checks.
-            // We iterate through all assets to create a map (cost: `(outAssetsNum + inAssetsNum) * tokenAccessCost)`)
-            // and after that we iterate through unique asset ids to check preservation rules (cost: `(inAssets.size + outAssets.size) * tokenAccessCost`)
-            val totalAssetsAccessCost = (outAssetsNum + inAssetsNum) * tokenAccessCost +
-              (inAssets.size + outAssets.size) * tokenAccessCost
-            val newCost = addExact(currentTxCost, totalAssetsAccessCost)
-
-            validation
-              // Check that transaction is not too costly considering all the assets
-              .validate(bsBlockTransactionsCost, maxCost >= newCost, s"$id: assets cost")
-              .validateSeq(outAssets) {
-                case (validationState, (outAssetId, outAmount)) =>
-                  val inAmount: Long = inAssets.getOrElse(outAssetId, -1L)
-
-                  // Check that for each asset output amount is no more than input amount,
-                  // with a possible exception for a new asset created by the transaction
-                  validationState.validate(txAssetsPreservation,
-                    inAmount >= outAmount || (outAssetId == newAssetId && outAmount > 0),
-                    s"$id: Amount in = $inAmount, out = $outAmount. Allowed new asset = $newAssetId, out = $outAssetId")
-              }
-              .payload(newCost)
-          case Failure(e) =>
-            // should never be here as far as we've already checked this when we've created the box
-            ModifierValidator.fatal(e.getMessage)
+    verifier.synchronized {
+      verifier.IR.resetContext() // ensure there is no garbage in the IRContext
+      lazy val inputSumTry = Try(boxesToSpend.map(_.value).reduce(Math.addExact(_, _)))
+
+      // Cost of transaction initialization: we should read and parse all inputs and data inputs,
+      // and also iterate through all outputs to check rules
+      val initialCost: Long = addExact(
+        CostTable.interpreterInitCost,
+        multiplyExact(boxesToSpend.size, stateContext.currentParameters.inputCost),
+        multiplyExact(dataBoxes.size, stateContext.currentParameters.dataInputCost),
+        multiplyExact(outputCandidates.size, stateContext.currentParameters.outputCost),
+      )
+      val maxCost = stateContext.currentParameters.maxBlockCost
+
+      ModifierValidator(stateContext.validationSettings)
+        // Check that the transaction is not too big
+        .validate(bsBlockTransactionsCost, maxCost >= addExact(initialCost, accumulatedCost), s"$id: initial cost")
+        // Starting validation
+        .payload(initialCost)
+        // Perform cheap checks first
+        .validateNoFailure(txAssetsInOneBox, outAssetsTry)
+        .validate(txPositiveAssets, outputCandidates.forall(_.additionalTokens.forall(_._2 > 0)), s"$id: ${outputCandidates.map(_.additionalTokens)}")
+        // Check that outputs are not dust, and not created in future
+        .validateSeq(outputs) { case (validationState, out) =>
+          validationState
+            .validate(txDust, out.value >= BoxUtils.minimalErgoAmount(out, stateContext.currentParameters), s"$id, output ${Algos.encode(out.id)}, ${out.value} >= ${BoxUtils.minimalErgoAmount(out, stateContext.currentParameters)}")
+            .validate(txFuture, out.creationHeight <= stateContext.currentHeight, s"$id: output $out")
+            .validate(txBoxSize, out.bytes.length <= MaxBoxSize.value, s"$id: output $out")
+            .validate(txBoxPropositionSize, out.propositionBytes.length <= MaxPropositionBytes.value, s"$id: output $out")
+        }
+        // Just to be sure, check that all the input boxes to spend (and to read) are presented.
+        // Normally, this check should always pass, if the client is implemented properly
+        // so it is not part of the protocol really.
+        .validate(txBoxesToSpend, boxesToSpend.size == inputs.size, s"$id: ${boxesToSpend.size} == ${inputs.size}")
+        .validate(txDataBoxes, dataBoxes.size == dataInputs.size, s"$id: ${dataBoxes.size} == ${dataInputs.size}")
+        // Check that there are no overflow in input and output values
+        .validate(txInputsSum, inputSumTry.isSuccess, s"$id")
+        // Check that transaction is not creating money out of thin air.
+        .validate(txErgPreservation, inputSumTry == outputsSumTry, s"$id: $inputSumTry == $outputsSumTry")
+        .validateTry(outAssetsTry, e => ModifierValidator.fatal("Incorrect assets", e)) { case (validation, (outAssets, outAssetsNum)) =>
+          ErgoTransaction.extractAssets(boxesToSpend) match {
+            case Success((inAssets, inAssetsNum)) =>
+              lazy val newAssetId = ByteArrayWrapper(inputs.head.boxId)
+              val tokenAccessCost = stateContext.currentParameters.tokenAccessCost
+              val currentTxCost = validation.result.payload.get
+              // Cost of assets preservation rules checks.
+              // We iterate through all assets to create a map (cost: `(outAssetsNum + inAssetsNum) * tokenAccessCost)`)
+              // and after that we iterate through unique asset ids to check preservation rules (cost: `(inAssets.size + outAssets.size) * tokenAccessCost`)
+              val totalAssetsAccessCost = (outAssetsNum + inAssetsNum) * tokenAccessCost +
+                (inAssets.size + outAssets.size) * tokenAccessCost
+              val newCost = addExact(currentTxCost, totalAssetsAccessCost)
+
+              validation
+                // Check that transaction is not too costly considering all the assets
+                .validate(bsBlockTransactionsCost, maxCost >= newCost, s"$id: assets cost")
+                .validateSeq(outAssets) {
+                  case (validationState, (outAssetId, outAmount)) =>
+                    val inAmount: Long = inAssets.getOrElse(outAssetId, -1L)
+
+                    // Check that for each asset output amount is no more than input amount,
+                    // with a possible exception for a new asset created by the transaction
+                    validationState.validate(txAssetsPreservation,
+                      inAmount >= outAmount || (outAssetId == newAssetId && outAmount > 0),
+                      s"$id: Amount in = $inAmount, out = $outAmount. Allowed new asset = $newAssetId, out = $outAssetId")
+                }
+                .payload(newCost)
+            case Failure(e) =>
+              // should never be here as far as we've already checked this when we've created the box
+              ModifierValidator.fatal(e.getMessage)
+          }
+        }
+        // Check inputs, the most expensive check usually, so done last.
+        .validateSeq(boxesToSpend.zipWithIndex) { case (validation, (box, idx)) =>
+          val currentTxCost = validation.result.payload.get
+
+          val input = inputs(idx)
+          val proof = input.spendingProof
+          val proverExtension = proof.extension
+          val transactionContext = TransactionContext(boxesToSpend, dataBoxes, this, idx.toShort)
+          val ctx = new ErgoContext(stateContext, transactionContext, proverExtension, maxCost - addExact(currentTxCost, accumulatedCost), 0)
+
+          val costTry = verifier.verify(box.ergoTree, ctx, proof, messageToSign)
+          costTry.recover { case t =>
+            log.debug(s"Tx verification failed: ${t.getMessage}")
+          }
+
+          lazy val (isCostValid, scriptCost) = costTry.getOrElse((false, maxCost + 1))
+
+          validation
+            // Just in case, should always be true if client implementation is correct.
+            .validateEquals(txBoxToSpend, box.id, input.boxId)
+            // Check whether input box script interpreter raised exception
+            .validate(txScriptValidation, costTry.isSuccess && isCostValid, s"$id: #$idx => $costTry")
+            // Check that cost of the transaction after checking the input becomes too big
+            .validate(bsBlockTransactionsCost, maxCost >= addExact(currentTxCost, accumulatedCost, scriptCost), s"$id: cost exceeds limit after input #$idx")
+            .map(c => addExact(c, scriptCost))
         }
-      }
-      // Check inputs, the most expensive check usually, so done last.
-      .validateSeq(boxesToSpend.zipWithIndex) { case (validation, (box, idx)) =>
-      val currentTxCost = validation.result.payload.get
-
-      val input = inputs(idx)
-      val proof = input.spendingProof
-      val proverExtension = proof.extension
-      val transactionContext = TransactionContext(boxesToSpend, dataBoxes, this, idx.toShort)
-      val ctx = new ErgoContext(stateContext, transactionContext, proverExtension, maxCost - addExact(currentTxCost, accumulatedCost), 0)
-
-      val costTry = verifier.verify(box.ergoTree, ctx, proof, messageToSign)
-      costTry.recover { case t =>
-        log.debug(s"Tx verification failed: ${t.getMessage}")
-      }
-
-      lazy val (isCostValid, scriptCost) = costTry.getOrElse((false, maxCost + 1))
-
-      validation
-        // Just in case, should always be true if client implementation is correct.
-        .validateEquals(txBoxToSpend, box.id, input.boxId)
-        // Check whether input box script interpreter raised exception
-        .validate(txScriptValidation, costTry.isSuccess && isCostValid, s"$id: #$idx => $costTry")
-        // Check that cost of the transaction after checking the input becomes too big
-        .validate(bsBlockTransactionsCost, maxCost >= addExact(currentTxCost, accumulatedCost, scriptCost), s"$id: cost exceeds limit after input #$idx")
-        .map(c => addExact(c, scriptCost))
     }
   }
 
```
