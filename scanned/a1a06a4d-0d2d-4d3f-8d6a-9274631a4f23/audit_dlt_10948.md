# [?] rv32im-m3: Fix for out of bounds access in bigint (#3538)

## Summary
Severity: Unknown
Chain: ZK
Component: risc0/risc0
Published: 2025-11-12
Source: https://github.com/risc0/risc0/commit/57fd1b069fb4afda0be36cac253b8054b080b67d
Type: security-commit

## Details
rv32im-m3: Fix for out of bounds access in bigint (#3538)

## Patch
### risc0/bigint2/Cargo.toml
```diff
@@ -38,4 +38,5 @@ cuda = ["risc0-zkvm/cuda"]
 default = []
 num-bigint-dig = ["dep:num-bigint-dig"]
 num-bigint = ["dep:num-bigint"]
+rv32im-m3 = ["risc0-zkvm/rv32im-m3"]
 unstable = []
```

### risc0/circuit/rv32im-m3-sys/build.rs
```diff
@@ -69,6 +69,12 @@ fn main() {
         .debug(false)
         .warnings(false)
         .flag("-std=c++17")
+        // .flag("-Xcompiler")
+        // .flag("-fsanitize=address")
+        // .flag("-Xcompiler")
+        // .flag("-fno-omit-frame-pointer")
+        // .flag("-Xcompiler")
+        // .flag("-g")
         .include("cxx")
         .include("vendor")
         .include(env::var("DEP_RISC0_SYS_CXX_ROOT").unwrap())
@@ -81,6 +87,8 @@ fn main() {
         .files(glob_paths("cxx/zkp/*.cpp"))
         .files(generated_files);
 
+    // println!("cargo:rustc-link-lib=asan");
+
     // if is_metal() {
     //     build
     //         .file("cxx/hal/metal/hal.cpp")
```

### risc0/circuit/rv32im-m3-sys/cxx/hal/cuda/hal.cpp
```diff
@@ -172,6 +172,14 @@ class CudaBuffer : public IBuffer {
   cudaStream_t stream;
 };
 
+template <typename... Types> inline std::string fmt(const char* fmt, Types... args) {
+  size_t len = std::snprintf(nullptr, 0, fmt, args...);
+  std::string ret(++len, '\0');
+  std::snprintf(&ret.front(), len, fmt, args...);
+  ret.resize(--len);
+  return ret;
+}
+
 using CudaBufferPtr = std::shared_ptr<CudaBuffer>;
 
 class CudaHal : public IHal {
@@ -191,10 +199,15 @@ class CudaHal : public IHal {
 
 public:
   CudaHal() {
-    if (!cuda_stream_create(&stream)) {
-      throw std::runtime_error("error during cudaStreamCreate");
+    // cudaStreamCreate(&stream);
+    cudaError_t err = cudaStreamCreate(&stream);
+    if (err != cudaSuccess) {
+      auto msg = fmt(
+          "cudaStreamCreate failed: \"%s\"\n%s:%d", cudaGetErrorString(err), __FILE__, __LINE__);
+      throw std::runtime_error{msg};
     }
   }
+
   ~CudaHal() override { (void)cuda_stream_destroy(stream); }
 
   void hashRows(HalArray<Digest> out, HalMatrix<Fp> in) override {
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/base/constants.h
```diff
@@ -24,6 +24,7 @@
 #endif
 
 // Very basic numbers
+CONSTANT uint32_t WORD_SIZE = 4;
 CONSTANT uint32_t BITS_PER_BYTE = 8;
 CONSTANT uint32_t BYTES_PER_WORD_PO2 = 2;
 CONSTANT uint32_t BYTES_PER_WORD = (1 << BYTES_PER_WORD_PO2);
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/emu/bigint.cpp
```diff
@@ -15,15 +15,15 @@
 
 #include "num/num.hpp"
 
-#include "rv32im/emu/bigint.h"
-
-#include "bigint.h"
 #include "rv32im/base/constants.h"
+#include "rv32im/emu/bigint.h"
 
 namespace risc0::rv32im {
 
 namespace {
 
+constexpr size_t BIGINT_WIDTH_BYTES = 16;
+
 using BigInt = Num;
 
 BigInt bigIntFromWords(std::vector<Num::word>&& words) {
@@ -255,7 +255,7 @@ BigInt BigIntIO::load(uint32_t arena, uint32_t offset, uint32_t count) {
     std::array<uint32_t, 4> words;
     for (size_t j = 0; j < 4; j++) {
       words[j] = peek(baseWord + i * 4 + j);
-      LOG(2, "host peek [" << (baseWord + i * 4 + j) << "] = " << words[j]);
+      LOG(3, "host peek [" << (baseWord + i * 4 + j) << "] = " << words[j]);
     }
     limbs64.push_back(uint64_t(words[0]) | ((uint64_t(words[1])) << 32));
     limbs64.push_back(uint64_t(words[2]) | ((uint64_t(words[3])) << 32));
@@ -285,9 +285,10 @@ void BigIntIO::store(uint32_t arena, uint32_t offset, uint32_t count, BigInt val
 
 size_t witgenBigInt(std::map<uint32_t, uint32_t>& polyWitness, PeekFunc peek) {
   // TODO: Proper error handling
-  uint32_t blobWordAddr = peek(MACHINE_REGS_WORD + REG_A0) / 4;
-  uint32_t bibcWordAddr = peek(MACHINE_REGS_WORD + REG_T1) / 4;
+  uint32_t blobWordAddr = peek(MACHINE_REGS_WORD + REG_A0) / WORD_SIZE;
+  uint32_t bibcWordAddr = peek(MACHINE_REGS_WORD + REG_T1) / WORD_SIZE;
   uint32_t bibcSize = peek(blobWordAddr);
+  uint32_t verifySize = peek(blobWordAddr + 1);
 
   std::vector<uint32_t> code;
   for (size_t i = 0; i < bibcSize; i++) {
@@ -300,24 +301,7 @@ size_t witgenBigInt(std::map<uint32_t, uint32_t>& polyWitness, PeekFunc peek) {
   BigIntIO io(mm, peek, polyWitness);
   prog.eval(io);
 
-  // Count # of steps
-  // TODO, should be have a max size, error handling?
-  size_t size = 0;
-  uint32_t progStart = peek(MACHINE_REGS_WORD + REG_T2) / 4;
-  while (true) {
-    auto decoded = BigIntInstruction::decode(peek(progStart + size));
-    // LOG(0, "Reading program @ " << progStart + size);
-    // LOG(0, "  polyOp = " << decoded.polyOp);
-    // LOG(0, "  memOp = " << decoded.memOp);
-    // LOG(0, "  coeff = " << decoded.coeff);
-    // LOG(0, "  reg = " << decoded.reg);
-    // LOG(0, "  offset = " << decoded.offset);
-    size++;
-    if (decoded.polyOp == 0) {
-      break;
-    }
-  }
-  return size;
+  return verifySize;
 }
 
 BytePolynomial::BytePolynomial() {}
@@ -391,36 +375,72 @@ std::ostream& operator<<(std::ostream& os, const BytePolynomial& x) {
   return os;
 }
 
+// Do carry propagation
+BytePolynomial BytePolynomial::propagateCarry() const {
+  BytePolynomial ret;
+  ret.coeffs = coeffs;
+
+  int32_t carry = 0;
+  for (size_t i = 0; i < ret.coeffs.size(); i++) {
+    ret.coeffs[i] += carry;
+    if (ret.coeffs[i] % 256 != 0) {
+      LOG(0, "totCarry[" << i << "]=" << ret.coeffs[i]);
+      throw std::runtime_error("Bad carry");
+    }
+    ret.coeffs[i] /= 256;
+    carry = ret.coeffs[i];
+  }
+
+  return ret;
+}
+
+BytePolynomial BytePolynomial::fromData(uint32_t* data) {
+  BytePolynomial ret;
+  ret.coeffs.resize(16);
+  for (size_t i = 0; i < 4; i++) {
+    for (size_t j = 0; j < 4; j++) {
+      ret.coeffs[i * 4 + j] = (data[i] >> (8 * j)) & 0xff;
+    }
+  }
+  return ret;
+}
+
+BytePolynomial BytePolynomial::negPoly() {
+  BytePolynomial ret;
+  ret.coeffs.resize(16, -128);
+  return ret;
+}
+
+BytePolynomial BytePolynomial::basisPoint() {
+  BytePolynomial ret;
+  ret.coeffs.push_back(-256);
+  ret.coeffs.push_back(1);
+  return ret;
+}
+
 BigIntPreflight::BigIntPreflight() : inCarry(false) {
   poly = BytePolynomial::zero();
   term = BytePolynomial::one();
   total = BytePolynomial::zero();
 }
 
 void BigIntPreflight::step(const BigIntInstruction& inst, uint32_t* data) {
-  if (inst.polyOp != 0 && inst.memOp == 2) {
+  if (inst.polyOp != static_cast<uint32_t>(PolyOp::NOP) &&
+      inst.memOp == static_cast<uint32_t>(MemoryOp::CHECK)) {
+    LOG(2, "MemoryOp::CHECK && !PolyOp::NOP");
     // Handle carry computation
     if (!inCarry) {
       // Transition to carry output, compute carry
-      totCarry = total;
-      int32_t carry = 0;
-      // Do carry propagation
-      for (size_t i = 0; i < totCarry.coeffs.size(); i++) {
-        totCarry.coeffs[i] += carry;
-        if (totCarry.coeffs[i] % 256 != 0) {
-          LOG(0, "totCarry.coeffs[" << i << "]=" << totCarry.coeffs[i]);
-          throw std::runtime_error("Bad carry");
-        }
-        totCarry.coeffs[i] /= 256;
-        carry = totCarry.coeffs[i];
-      }
+      totCarry = total.propagateCarry();
       inCarry = true;
     }
+
     // Output carry to ret
-    uint8_t ret[16];
+    uint8_t ret[BIGINT_WIDTH_BYTES];
     int32_t basePoint = 128 * 256 * 64;
-    for (size_t i = 0; i < 16; i++) {
-      uint32_t val = totCarry.coeffs[inst.offset * 16 + i] + basePoint;
+    LOG(2, "totCarry: " << totCarry.size());
+    for (size_t i = 0; i < BIGINT_WIDTH_BYTES; i++) {
+      uint32_t val = totCarry[inst.offset * BIGINT_WIDTH_BYTES + i] + basePoint;
       switch (PolyOp(inst.polyOp)) {
       case PolyOp::CARRY_1:
         ret[i] = (val >> 14) & 0xff;
@@ -433,9 +453,10 @@ void BigIntPreflight::step(const BigIntInstruction& inst, uint32_t* data) {
         ret[i] = val & 0xff;
         break;
       default:
-        throw std::runtime_error("Invalid memOp=2 operation");
+        throw std::runtime_error("Invalid polyOp with MemoryOp_Check");
       }
     }
+
     // Write to data
     for (size_t i = 0; i < 4; i++) {
       uint32_t val = 0;
@@ -445,53 +466,52 @@ void BigIntPreflight::step(const BigIntInstruction& inst, uint32_t* data) {
       data[i] = val;
     }
   }
+
   // Expand data into a byte poly
-  BytePolynomial local;
-  local.coeffs.resize(16);
-  for (size_t i = 0; i < 4; i++) {
-    for (size_t j = 0; j < 4; j++) {
-      local.coeffs[i * 4 + j] = (data[i] >> (8 * j)) & 0xff;
-    }
-  }
+  BytePolynomial local = BytePolynomial::fromData(data);
+
   // Precompute some values
-  BytePolynomial negPoly;
-  negPoly.coeffs.resize(16, -128);
   BytePolynomial newPoly = poly + local;
-  BytePolynomial bp;
-  bp.coeffs.push_back(-256);
-  bp.coeffs.push_back(1);
   int32_t coeff = int32_t(inst.coeff) - 4;
+
   // Apply the poly-op
   switch (PolyOp(inst.polyOp)) {
   case PolyOp::NOP:
+    LOG(2, "NOP");
     poly = BytePolynomial::zero();
     term = BytePolynomial::one();
     total = BytePolynomial::zero();
     inCarry = false;
     break;
   case PolyOp::SHIFT:
+    LOG(2, "SHIFT");
     poly = newPoly.shift();
     break;
   case PolyOp::SET_TERM:
+    LOG(2, "SET_TERM");
     poly = BytePolynomial::zero();
     term = newPoly;
     break;
   case PolyOp::ADD_TOTAL:
+    LOG(2, "ADD_TOTAL");
     total = total + newPoly * term * coeff;
     term = BytePolynomial::one();
     poly = BytePolynomial::zero();
     break;
   case PolyOp::CARRY_1:
-    poly = poly + (local + negPoly) * 64 * 256;
+    LOG(2, "CARRY_1");
+    poly = poly + (local + BytePolynomial::negPoly()) * 64 * 256;
     break;
   case PolyOp::CARRY_2:
+    LOG(2, "CARRY_1");
     poly = poly + local * 256;
     break;
   case PolyOp::EQZ:
-    total = total + bp * newPoly;
-    for (size_t i = 0; i < total.coeffs.size(); i++) {
-      if (total.coeffs[i] != 0) {
-        LOG(0, "Coeffs[" << i << "]=" << total.coeffs[i]);
+    LOG(2, "EQZ");
+    total = total + BytePolynomial::basisPoint() * newPoly;
+    for (size_t i = 0; i < total.size(); i++) {
+      if (total[i] != 0) {
+        LOG(0, "Coeffs[" << i << "]=" << total[i]);
         throw std::runtime_error("INVALID EQZ");
       }
     }
@@ -501,12 +521,12 @@ void BigIntPreflight::step(const BigIntInstruction& inst, uint32_t* data) {
     inCarry = false;
     break;
   }
-  // LOG(0, "PolyOp = " << inst.polyOp);
-  // LOG(0, "  local = " << local);
-  // LOG(0, "  newPoly = " << newPoly);
-  // LOG(0, "  poly = " << poly);
-  // LOG(0, "  term = " << term);
-  // LOG(0, "  total = " << total);
+  LOG(3, "PolyOp = " << inst.polyOp);
+  LOG(3, "  local = " << local);
+  LOG(3, "  newPoly = " << newPoly);
+  LOG(3, "  poly = " << poly);
+  LOG(3, "  term = " << term);
+  LOG(3, "  total = " << total);
 }
 
 } // namespace risc0::rv32im
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/emu/bigint.h
```diff
@@ -48,16 +48,35 @@ struct BigIntInstruction {
 // of validate
 size_t witgenBigInt(std::map<uint32_t, uint32_t>& polyWitness, PeekFunc peek);
 
-struct BytePolynomial {
+class BytePolynomial {
+public:
   BytePolynomial();
   static BytePolynomial zero();
   static BytePolynomial one();
+  static BytePolynomial negPoly();
+  static BytePolynomial basisPoint();
+  static BytePolynomial fromData(uint32_t* data);
+
   BytePolynomial shift() const;
   BytePolynomial operator*(int x) const;
   BytePolynomial operator+(const BytePolynomial& rhs) const;
   BytePolynomial operator*(const BytePolynomial& rhs) const;
 
+  size_t size() const { return coeffs.size(); }
+
+  int32_t operator[](size_t x) const {
+    if (x < coeffs.size()) {
+      return coeffs[x];
+    }
+    return 0;
+  }
+
+  BytePolynomial propagateCarry() const;
+
+private:
   std::vector<int32_t> coeffs;
+
+  friend std::ostream& operator<<(std::ostream& os, const BytePolynomial& x);
 };
 
 std::ostream& operator<<(std::ostream& os, const BytePolynomial& x);
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/emu/emu.cpp
```diff
@@ -29,7 +29,7 @@ namespace risc0::rv32im {
 
 namespace {
 
-#define DLOG(...) LOG(2, __VA_ARGS__)
+#define DLOG(...) LOG(3, __VA_ARGS__)
 // #define DLOG(...) /**/
 
 constexpr uint32_t CYCLE_TABLE_ROWS = 24;
@@ -745,7 +745,7 @@ struct Emulator {
   void do_ECALL_BIG_INT() {
     std::map<uint32_t, uint32_t> polyWitness;
     size_t count = witgenBigInt(polyWitness, [&](uint32_t addr) { return peekPhysMemory(addr); });
-    LOG(1, "BIGINT ecall with count = " << count);
+    LOG(2, "BIGINT ecall with count = " << count);
     // TODO: Based on count + polyWitness paging, decide if we need to abort
     auto& wit = trace.makeEcallBigInt();
     wit.cycle = curCycle;
@@ -757,6 +757,7 @@ struct Emulator {
     curCycle++;
     BigIntPreflight pf;
     for (size_t i = 0; i < count; i++) {
+      LOG(2, "BigIntPreflight: " << i);
       auto& biWit = trace.makeBigInt();
       biWit.cycle = curCycle;
       biWit.mm = biMm;
@@ -943,7 +944,7 @@ bool emulate(Trace& trace, MemoryImage& image, HostIO& io, size_t rowCount, uint
   Emulator emu(trace, image, io, rowCount);
   emu.addTables();
   bool done = emu.run(rowCount, endCycle);
-  LOG(1, "Cycle = " << emu.curCycle);
+  LOG(2, "Cycle = " << emu.curCycle);
   emu.commit();
   return done;
 }
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/emu/paging.cpp
```diff
@@ -53,7 +53,7 @@ void PagedMemory::commit(const std::vector<PageDetails*>& pages) {
   // Page in all the pages that were read
   auto itNodeEnd = loaded.lower_bound(MEMORY_SIZE_MPAGES);
   for (auto it = itNodeEnd; it != loaded.end(); ++it) {
-    LOG(2, "Paging in: " << *it - MEMORY_SIZE_MPAGES);
+    LOG(3, "Paging in: " << *it - MEMORY_SIZE_MPAGES);
     pageInPage(*it - MEMORY_SIZE_MPAGES);
   }
   // Page in all nodes that were read
@@ -63,7 +63,7 @@ void PagedMemory::commit(const std::vector<PageDetails*>& pages) {
   // Page out all the new pages, update image
   for (auto it = loaded.lower_bound(MEMORY_SIZE_MPAGES); it != loaded.end(); ++it) {
     size_t page = *it - MEMORY_SIZE_MPAGES;
-    LOG(2, "Paging out: " << page);
+    LOG(3, "Paging out: " << page);
     pageOutPage(page, pages[page]);
   }
   // Page out all  nodes
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/ffi.cpp
```diff
@@ -116,7 +116,7 @@ class ReplayHostIO : public HostIO {
 public:
   uint32_t onWrite(uint32_t fd, const uint8_t* data, uint32_t size) override {
     size_t bytes = writes[curWrite++];
-    LOG(2, "onWrite: " << bytes << " bytes");
+    LOG(3, "onWrite: " << bytes << " bytes");
     return bytes;
   }
 
@@ -125,7 +125,7 @@ class ReplayHostIO : public HostIO {
     if (size < record.size()) {
       throw std::runtime_error("Read record too big");
     }
-    LOG(2, "onRead: " << record.size() << " bytes");
+    LOG(3, "onRead: " << record.size() << " bytes");
     std::memcpy(data, record.data(), record.size());
     return record.size();
   }
```

### risc0/circuit/rv32im-m3-sys/cxx/rv32im/witness/bigint.h
```diff
@@ -17,6 +17,12 @@
 
 #include "rv32im/witness/mem.h"
 
+enum class MemoryOp {
+  READ = 0,
+  WRITE = 1,
+  CHECK = 2,
+};
+
 enum class PolyOp {
   NOP = 0,
   SHIFT = 1,
```
