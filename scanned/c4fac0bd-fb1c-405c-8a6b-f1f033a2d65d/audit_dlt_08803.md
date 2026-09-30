# [?] prevent overflow

## Summary
Severity: Unknown
Chain: Linea
Component: LFDT-Lineth/lineth-monorepo
Published: 2023-03-28
Source: https://github.com/LFDT-Lineth/lineth-monorepo/commit/5f2863931ffde4768bd0ef2098ff5e6605e96959
Type: security-commit

## Details
prevent overflow

Signed-off-by: Sally MacFarlane <macfarla.github@gmail.com>

## Patch
### tracer/src/main/java/net/consensys/zktracer/module/alu/add/Adder.java
```diff
@@ -26,11 +26,23 @@ public class Adder {
 
   public static Bytes32 addSub(final OpCode opCode, final Bytes32 value, final Bytes32 value2) {
     LOG.info("adding " + value + " " + opCode.name() + " " + value2);
-    return switch (opCode) {
-      case ADD -> Bytes32.leftPad(Bytes.of(value.toBigInteger().add(value2.toBigInteger()).toByteArray()));
-      case SUB -> Bytes32.leftPad(Bytes.of(value.toBigInteger().subtract(value2.toBigInteger()).toByteArray()));
-      default -> Bytes32.ZERO; // TODO what should happen here
-    };
+    final BigInteger res = x(opCode, value, value2);
+    // ensure result is correct length
+    final Bytes resBytes = Bytes.of(res.toByteArray());
+    if (resBytes.size() > 32 ) {
+      return Bytes32.wrap(resBytes, resBytes.size() - 32);
+    }
+    return Bytes32.leftPad(Bytes.of(res.toByteArray()));
+  }
+
+  private static BigInteger x(final OpCode opCode, final Bytes32 value, final Bytes32 value2) {
+    {
+      return switch (opCode) {
+        case ADD -> value.toBigInteger().add(value2.toBigInteger());
+        case SUB -> value.toBigInteger().subtract(value2.toBigInteger());
+        default -> BigInteger.ZERO; // TODO what should happen here
+      };
+    }
   }
 
 }
```

### tracer/src/test/java/net/consensys/zktracer/module/alu/add/AdderTest.java
```diff
@@ -30,4 +30,28 @@ void xAddZero_isX() {
         Bytes32 actual = Adder.addSub(OpCode.ADD, randomBytes, Bytes32.ZERO);
         assertThat(actual).isEqualTo(randomBytes);
     }
+    @Test
+    void maxSubMax_isZero() {
+        byte b;
+        b = 'f';
+        Bytes32 max = Bytes32.repeat(b);
+        Bytes32 actual = Adder.addSub(OpCode.SUB, max, max);
+        assertThat(actual).isEqualTo(Bytes32.ZERO);
+    }
+    @Test
+    void maxSubZero_isMax() {
+        byte b;
+        b = 'f';
+        Bytes32 max = Bytes32.repeat(b);
+        Bytes32 actual = Adder.addSub(OpCode.SUB, max, Bytes32.ZERO);
+        assertThat(actual).isEqualTo(max);
+    }
+    @Test
+    void overflowDoesNotError() {
+        byte b;
+        b = '9';
+        Bytes32 max = Bytes32.repeat(b);
+        Bytes32 actual = Adder.addSub(OpCode.ADD, max, max);
+        assertThat(actual).isEqualTo(max);
+    }
 }
\ No newline at end of file
```
