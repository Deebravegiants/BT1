# [?] Fix mem free crash and progress on Circom integration

## Summary
Severity: Unknown
Chain: Polygon zkEVM
Component: 0xPolygon/zkevm-prover
Published: 2022-01-12
Source: https://github.com/0xPolygon/zkevm-prover/commit/2680797b4819670b4b4df5e61526d38c9d669bed
Type: security-commit

## Details
Fix mem free crash and progress on Circom integration

## Patch
### src/batchmachine_executor.cpp
```diff
@@ -527,33 +527,90 @@ function refToObject(F, mem, ref) {
 
 json BatchMachineExecutor::refToObject (const Mem &mem, const Reference &ref)
 {
+    zkassert(mem[ref.id].type == ref.type);
+
+    json j;
+
     switch (ref.type)
     {
     case rt_int:
     {
-        return mem[ref.id].integer;
+        j = mem[ref.id].integer;
+        break;
     }
     case rt_field:
     {
         RawFr::Element fe = mem[ref.id].fe; // TODO: pass mem[ref.id].fe directly when finite fields library supports const parameters
-        return fr.toString(fe, 16);
+        j = NormalizeToNFormat(fr.toString(fe, 16), 64);
+        break;
     }
     case rt_pol:
     {
-        json j;
         for (uint64_t i = 0; i < ref.N; i++)
         {
-            j.push_back(fr.toString(mem[ref.id].pPol[i], 16));
+            j.push_back(NormalizeToNFormat(fr.toString(mem[ref.id].pPol[i], 16), 64));
         }
+        break;
     }
+    /*case rt_treeGroup:
+    {
+        uint64_t size = ref.memSize / sizeof(RawFr::Element);
+        for (uint64_t i = 0; i < size; i++)
+        {
+            j.push_back(NormalizeToNFormat(fr.toString(mem[ref.id].pTreeGroup[i], 16), 64));
+        }
+        break;
+    }*/
     case rt_treeGroup_groupProof:
+    {
+        uint64_t size = ref.memSize / sizeof(RawFr::Element);
+        for (uint64_t i = 0; i < size; i++)
+        {
+            j.push_back(NormalizeToNFormat(fr.toString(mem[ref.id].pTreeGroup_groupProof[i], 16), 64));
+        }
+        break;
+    }
     case rt_treeGroup_elementProof:
+    {
+        uint64_t size = ref.memSize / sizeof(RawFr::Element);
+        for (uint64_t i = 0; i < size; i++)
+        {
+            j.push_back(NormalizeToNFormat(fr.toString(mem[ref.id].pTreeGroup_elementProof[i], 16), 64));
+        }
+        break;
+    }
+    /*case rt_treeGroupMultipol:
+    {
+        uint64_t size = ref.memSize / sizeof(RawFr::Element);
+        for (uint64_t i = 0; i < size; i++)
+        {
+            j.push_back(NormalizeToNFormat(fr.toString(mem[ref.id].pTreeGroupMultipol[i], 16), 64));
+        }
+        break;
+    }*/
     case rt_treeGroupMultipol_groupProof:
-        return "TODO";
+    {
+        uint64_t size = ref.memSize / sizeof(RawFr::Element);
+        for (uint64_t i = 0; i < size; i++)
+        {
+            j.push_back(NormalizeToNFormat(fr.toString(mem[ref.id].pTreeGroupMultipol_groupProof[i], 16), 64));
+        }
+        break;
+    }
+    /*case rt_idxArray:
+    {
+        uint64_t size = ref.memSize / sizeof(RawFr::Element);
+        for (uint64_t i = 0; i < size; i++)
+        {
+            j.push_back(mem[ref.id].pIdxArray[i]);
+        }
+        break;
+    }*/ 
     default:
         cerr << "Error: refToObject cannot return JSON object of ref.type: " << ref.type << endl;
         exit(-1);
     }
+    return j;
 }
 
 void BatchMachineExecutor::calculateH1H2 (Reference &f, Reference &t, Reference &h1, Reference &h2)
```

### src/main.cpp
```diff
@@ -257,6 +257,8 @@ int main(int argc, char **argv)
     string cmPolsOutputFile(pOutputFile);
     string constPolsInputFile(pConstantsFile);
     string constTreePolsInputFile(pConstantsTreeFile);
+    string inputFile(pInputFile);
+    string witnessFile(pWitnessFile);
 
     TimerStopAndLog(PARSE_JSON_FILES);
 
@@ -305,7 +307,7 @@ int main(int argc, char **argv)
     TimerStopAndLog(SCRIPT_PARSE);
 
     // Create the prover
-    Prover prover(fr, romData, script, pil, constPols, cmPolsOutputFile, constTreePolsInputFile);
+    Prover prover(fr, romData, script, pil, constPols, cmPolsOutputFile, constTreePolsInputFile, inputFile, witnessFile);
 
 #ifdef RUN_GRPC_SERVER
     // Create server instance, passing all constant data
```

### src/mem.cpp
```diff
@@ -187,8 +187,10 @@ void MemFree(Mem &mem)
         }
         case rt_treeGroupMultipol:
         {
-            zkassert(mem[i].pTreeGroupMultipol != NULL);
-            free(mem[i].pTreeGroupMultipol);
+            if (mem[i].pTreeGroupMultipol != NULL)
+            {
+                free(mem[i].pTreeGroupMultipol);
+            }
             break;
         }
         case rt_treeGroupMultipol_groupProof:
@@ -314,4 +316,12 @@ void MemCopyPols(RawFr &fr, Mem &mem, const Pols &cmPols, const Pols &constPols,
         zkassert(mem[ref].N == NEVALUATIONS);
         CopyPol2Reference(fr, mem[ref], cmPols.orderedPols[i]);
     }
+}
+
+void MemUncopyPols(RawFr &fr, Mem &mem, const Pols &cmPols, const Pols &constPols, const string &constTreePolsInputFile)
+{
+    // TODO: Undo this:
+    // mem[treeReference].pTreeGroupMultipol = MerkleGroupMultiPol::fileToMap(constTreePolsInputFile, mem[treeReference].pTreeGroupMultipol, &M, mem[treeReference].nGroups, mem[treeReference].groupSize, mem[treeReference].nPols);
+    uint32_t treeReference = constPols.size;
+    mem[treeReference].pTreeGroupMultipol = NULL;
 }
\ No newline at end of file
```

### src/mem.hpp
```diff
@@ -15,5 +15,6 @@ typedef vector<Reference> Mem;
 void MemAlloc(Mem &mem, const Script &script);
 void MemFree(Mem &mem);
 void MemCopyPols(RawFr &fr, Mem &mem, const Pols &cmPols, const Pols &constPols, const string &constTreePolsInputFile);
+void MemUncopyPols(RawFr &fr, Mem &mem, const Pols &cmPols, const Pols &constPols, const string &constTreePolsInputFile);
 
 #endif
\ No newline at end of file
```

### src/output.hpp
```diff
@@ -10,7 +10,7 @@ class Output
 {
 public:
     string name;
-    Reference ref; // Contains data if array.size()==0
+    Reference ref; // Contains data if array.size()==0 and objects.size()==0
     vector<Output> array;
     vector<Output> objects;
     bool isArray (void) const { return array.size() > 0; }
```

### src/proof2zkin.cpp
```diff
@@ -14,13 +14,13 @@ void proof2zkin(const json &p, json &zkin)
     zkassert(p.size() >= 4);
 
     zkin["s0_rootUp1"] = p[0];
-    cout << zkin["s0_rootUp1"].dump() << endl;
+    //cout << zkin["s0_rootUp1"].dump() << endl;
     zkin["s0_rootUp2"] = p[1];
-    cout << zkin["s0_rootUp2"].dump() << endl;
+    //cout << zkin["s0_rootUp2"].dump() << endl;
     zkin["s0_rootUp3"] = p[2];
-    cout << zkin["s0_rootUp3"].dump() << endl;
+    //cout << zkin["s0_rootUp3"].dump() << endl;
     json friProof = p[3];
-    cout << "friProof:" << friProof.dump() << endl;
+    //cout << "friProof:" << friProof.dump() << endl;
 
     zkin["s0_valsUp1"] = json::array();
     zkin["s0_valsUp2"] = json::array();
@@ -42,13 +42,13 @@ void proof2zkin(const json &p, json &zkin)
     zkin["s0_siblingsDownA"] = json::array();
     zkin["s0_siblingsDownB"] = json::array();
 
-    cout << "friProof[0]:" << friProof.dump() << endl;
+    //cout << "friProof[0]:" << friProof.dump() << endl;
 
     json stepProof = friProof[0];
     zkin["s0_rootDown"] = stepProof["root2"];
     json polQueries = stepProof["polQueries"];
     zkassert(polQueries.is_array());
-    cout << "polQueries:" << polQueries.dump() << endl;
+    //cout << "polQueries:" << polQueries.dump() << endl;
     for (uint64_t i=0; i<stepProof["polQueries"].size(); i++)
     {
         zkin["s0_valsUp1"][i] = stepProof["polQueries"][i][0][0];
```

### src/prover.cpp
```diff
@@ -1,7 +1,13 @@
+#include <fstream>
+#include <iomanip>
 #include "prover.hpp"
 #include "utils.hpp"
 #include "mem.hpp"
 #include "batchmachine_executor.hpp"
+#include "proof2zkin.hpp"
+#include "verifier_cpp/main.hpp"
+
+using namespace std;
 
 void Prover::prove (const Input &input)
 {
@@ -28,9 +34,9 @@ void Prover::prove (const Input &input)
     MemAlloc(mem, script);
     TimerStopAndLog(MEM_ALLOC);
 
-    TimerStart(MEM_COPY);
+    TimerStart(MEM_COPY_POLS);
     MemCopyPols(fr, mem, cmPols, constPols, constTreePolsInputFile);
-    TimerStopAndLog(MEM_COPY);
+    TimerStopAndLog(MEM_COPY_POLS);
 
     TimerStart(BM_EXECUTOR);
     json starkProof;
@@ -45,11 +51,11 @@ void Prover::prove (const Input &input)
     TimerStart(PROOF2ZKIN);
 
     json zkin;
-    //proof2zkin(starkProof, zkin);
+    proof2zkin(starkProof, zkin);
 
-    //ofstream o("zkin.json");
-    //o << setw(4) << zkin << endl;
-    //o.close();
+    ofstream o("zkin.json");
+    o << setw(4) << zkin << endl;
+    o.close();
 
     TimerStopAndLog(PROOF2ZKIN);
 
@@ -58,19 +64,19 @@ void Prover::prove (const Input &input)
     /************/
 
     // TODO: Should we save zkin to file and use it as input file for the verifier?
-    /*
-    Circom_Circuit *circuit = loadCircuit("zkin.json"); // proof.json
+    
+    /*Circom_Circuit *circuit = loadCircuit("zkin.json"); // proof.json
     Circom_CalcWit *ctx = new Circom_CalcWit(circuit);
  
-    loadJson(ctx, pInputFile);
+    loadJson(ctx, inputFile);
     if (ctx->getRemaingInputsToBeSet()!=0) {
         cerr << "Error: Not all inputs have been set. Only " << get_main_input_signal_no()-ctx->getRemaingInputsToBeSet() << " out of " << get_main_input_signal_no() << endl;
         exit(-1);
     }
 
-    writeBinWitness(ctx, pWitnessFile); // No need to write the file to disk, 12-13M fe, in binary, in wtns format
-
-    Generate Groth16 via rapid SNARK
+    writeBinWitness(ctx, witnessFile); // No need to write the file to disk, 12-13M fe, in binary, in wtns format
+    */
+    /*Generate Groth16 via rapid SNARK
 
      "Usage: prove <circuit.zkey> (Jordi to provide) <witness.wtns> (from circom) <proof.json> (output, small, to return via gRPC) <public.json> (output, not needed, contains public input)\n";
     */
@@ -79,6 +85,10 @@ void Prover::prove (const Input &input)
     /* Cleanup */
     /***********/
 
+    TimerStart(MEM_UNCOPY_POLS);
+    MemUncopyPols(fr, mem, cmPols, constPols, constTreePolsInputFile);
+    TimerStopAndLog(MEM_UNCOPY_POLS);
+
     MemFree(mem);
     cmPols.unmap();
 }
\ No newline at end of file
```

### src/prover.hpp
```diff
@@ -17,9 +17,11 @@ class Prover
     const Pols &constPols;
     const string &cmPolsOutputFile;
     const string &constTreePolsInputFile;
+    const string &inputFile;
+    const string &witnessFile;
 public:
-    Prover(RawFr &fr, const Rom &romData, const Script &script, const Pil &pil, const Pols &constPols, const string &cmPolsOutputFile, const string &constTreePolsInputFile) :
-        fr(fr), romData(romData), executor(fr, romData), script(script), pil(pil), constPols(constPols), cmPolsOutputFile(cmPolsOutputFile), constTreePolsInputFile(constTreePolsInputFile) {};
+    Prover(RawFr &fr, const Rom &romData, const Script &script, const Pil &pil, const Pols &constPols, const string &cmPolsOutputFile, const string &constTreePolsInputFile, const string &inputFile, const string &witnessFile) :
+        fr(fr), romData(romData), executor(fr, romData), script(script), pil(pil), constPols(constPols), cmPolsOutputFile(cmPolsOutputFile), constTreePolsInputFile(constTreePolsInputFile), inputFile(inputFile), witnessFile(witnessFile) {};
 
     void prove (const Input &input);
 };
```
