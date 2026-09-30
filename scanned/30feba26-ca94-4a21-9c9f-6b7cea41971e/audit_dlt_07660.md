# [?] Refactored SizeExtensions to avoid overflow (#4849)

## Summary
Severity: Unknown
Chain: Ethereum
Component: NethermindEth/nethermind
Published: 2022-11-02
Source: https://github.com/NethermindEth/nethermind/commit/ed6ccf549c046a8bb641d116fe144ed283983b1e
Type: security-commit

## Details
Refactored SizeExtensions to avoid overflow (#4849)

## Patch
### src/Nethermind/Nethermind.Core.Test/SizeExtensionsTests.cs
```diff
@@ -0,0 +1,43 @@
+//  Copyright (c) 2021 Demerzel Solutions Limited
+//  This file is part of the Nethermind library.
+// 
+//  The Nethermind library is free software: you can redistribute it and/or modify
+//  it under the terms of the GNU Lesser General Public License as published by
+//  the Free Software Foundation, either version 3 of the License, or
+//  (at your option) any later version.
+// 
+//  The Nethermind library is distributed in the hope that it will be useful,
+//  but WITHOUT ANY WARRANTY; without even the implied warranty of
+//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+//  GNU Lesser General Public License for more details.
+// 
+//  You should have received a copy of the GNU Lesser General Public License
+//  along with the Nethermind. If not, see <http://www.gnu.org/licenses/>.
+
+using System;
+using FluentAssertions;
+using Nethermind.Core.Extensions;
+using NUnit.Framework;
+
+namespace Nethermind.Core.Test
+{
+    [TestFixture]
+    public class SizeExtensionsTests
+    {
+        [TestCase(0)]
+        [TestCase(1000)]
+        [TestCase(9223372036)] // Int64.MaxValue / 1_000_000_000
+        public void CheckOverflow_long(long testCase)
+        {
+            Assert.IsTrue(testCase.GB() >= 0);
+        }
+
+        [TestCase(0)]
+        [TestCase(1000)]
+        [TestCase(2147483647)] // Int32.MaxValue
+        public void CheckOverflow_int(int testCase)
+        {
+            Assert.IsTrue(testCase.GB() >= 0);
+        }
+    }
+}
```

### src/Nethermind/Nethermind.Core/Extensions/IntExtensions.cs
```diff
@@ -20,69 +20,6 @@
 
 namespace Nethermind.Core.Extensions
 {
-    public static class SizeExtensions
-    {
-        public static long GB(this int @this)
-        {
-            return @this * 1_000_000_000L;
-        }
-
-        public static long MB(this int @this)
-        {
-            return @this * 1_000_000L;
-        }
-
-        public static long KB(this int @this)
-        {
-            return @this * 1_000L;
-        }
-
-        public static long GiB(this int @this)
-        {
-            return @this * 1024L * 1024L * 1024L;
-        }
-
-        public static long MiB(this int @this)
-        {
-            return @this * 1024L * 1024L;
-        }
-
-        public static long KiB(this int @this)
-        {
-            return @this * 1024L;
-        }
-
-        public static long GB(this long @this)
-        {
-            return ((int)@this).GB();
-        }
-
-        public static long MB(this long @this)
-        {
-            return ((int)@this).MB();
-        }
-
-        public static long KB(this long @this)
-        {
-            return ((int)@this).KB();
-        }
-
-        public static long GiB(this long @this)
-        {
-            return ((int)@this).GiB();
-        }
-
-        public static long MiB(this long @this)
-        {
-            return ((int)@this).MiB();
-        }
-
-        public static long KiB(this long @this)
-        {
-            return ((int)@this).KiB();
-        }
-    }
-
     public static class IntExtensions
     {
         public static string ToHexString(this int @this)
```

### src/Nethermind/Nethermind.Core/Extensions/SizeExtensions.cs
```diff
@@ -0,0 +1,85 @@
+//  Copyright (c) 2021 Demerzel Solutions Limited
+//  This file is part of the Nethermind library.
+// 
+//  The Nethermind library is free software: you can redistribute it and/or modify
+//  it under the terms of the GNU Lesser General Public License as published by
+//  the Free Software Foundation, either version 3 of the License, or
+//  (at your option) any later version.
+// 
+//  The Nethermind library is distributed in the hope that it will be useful,
+//  but WITHOUT ANY WARRANTY; without even the implied warranty of
+//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
+//  GNU Lesser General Public License for more details.
+// 
+//  You should have received a copy of the GNU Lesser General Public License
+//  along with the Nethermind. If not, see <http://www.gnu.org/licenses/>.
+
+using System;
+using System.Buffers.Binary;
+using Nethermind.Int256;
+
+namespace Nethermind.Core.Extensions
+{
+    public static class SizeExtensions
+    {
+        public static long GB(this long @this)
+        {
+            return @this * 1_000_000_000L;
+        }
+
+        public static long MB(this long @this)
+        {
+            return @this * 1_000_000L;
+        }
+
+        public static long KB(this long @this)
+        {
+            return @this * 1_000L;
+        }
+
+        public static long GiB(this long @this)
+        {
+            return @this * 1024L * 1024L * 1024L;
+        }
+
+        public static long MiB(this long @this)
+        {
+            return @this * 1024L * 1024L;
+        }
+
+        public static long KiB(this long @this)
+        {
+            return @this * 1024L;
+        }
+
+        public static long GB(this int @this)
+        {
+            return ((long)@this).GB();
+        }
+
+        public static long MB(this int @this)
+        {
+            return ((long)@this).MB();
+        }
+
+        public static long KB(this int @this)
+        {
+            return ((long)@this).KB();
+        }
+
+        public static long GiB(this int @this)
+        {
+            return ((long)@this).GiB();
+        }
+
+        public static long MiB(this int @this)
+        {
+            return ((long)@this).MiB();
+        }
+
+        public static long KiB(this int @this)
+        {
+            return ((long)@this).KiB();
+        }
+    }
+}
```
