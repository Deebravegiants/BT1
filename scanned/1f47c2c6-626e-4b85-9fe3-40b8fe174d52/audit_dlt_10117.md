# [?] 1. Fix the crash in p2p protocol;

## Summary
Severity: Unknown
Chain: Neo
Component: neo-project/neo
Published: 2017-02-24
Source: https://github.com/neo-project/neo/commit/96169d71341bb416ad72bba733ab560881e017a7
Type: security-commit

## Details
1. Fix the crash in p2p protocol;
2. Improve performance;
3. Verify transactions parallelly;
4. Rename some variables;

## Patch
### src/AntShares/Consensus/ConsensusService.cs
```diff
@@ -31,10 +31,10 @@ public ConsensusService(LocalNode localNode, Wallet wallet, string log_dictionar
             this.log_dictionary = log_dictionary;
         }
 
-        private bool AddTransaction(Transaction tx)
+        private bool AddTransaction(Transaction tx, bool verify)
         {
             if (Blockchain.Default.ContainsTransaction(tx.Hash) ||
-                !tx.Verify(context.Transactions.Values) ||
+                (verify && !tx.Verify(context.Transactions.Values)) ||
                 !CheckPolicy(tx))
             {
                 Log($"reject tx: {tx.Hash}{Environment.NewLine}{tx.ToArray().ToHexString()}");
@@ -149,7 +149,7 @@ private static ulong GetNonce()
             byte[] nonce = new byte[sizeof(ulong)];
             Random rand = new Random();
             rand.NextBytes(nonce);
-            return BitConverter.ToUInt64(nonce, 0);
+            return nonce.ToUInt64(0);
         }
 
         private void InitializeConsensus(byte view_number)
@@ -220,7 +220,7 @@ private void LocalNode_NewInventory(object sender, IInventory inventory)
                         return;
                     if (context.Transactions.ContainsKey(tx.Hash)) return;
                     if (!context.TransactionHashes.Contains(tx.Hash)) return;
-                    AddTransaction(tx);
+                    AddTransaction(tx, true);
                 }
             }
         }
@@ -268,12 +268,12 @@ private void OnPerpareRequestReceived(ConsensusPayload payload, PerpareRequest m
             if (!context.MakeHeader().VerifySignature(context.Miners[payload.MinerIndex], message.Signature)) return;
             context.Signatures = new byte[context.Miners.Length][];
             context.Signatures[payload.MinerIndex] = message.Signature;
-            if (!AddTransaction(message.MinerTransaction)) return;
             Dictionary<UInt256, Transaction> mempool = LocalNode.GetMemoryPool().ToDictionary(p => p.Hash);
             foreach (UInt256 hash in context.TransactionHashes.Skip(1))
                 if (mempool.ContainsKey(hash))
-                    if (!AddTransaction(mempool[hash]))
+                    if (!AddTransaction(mempool[hash], false))
                         return;
+            if (!AddTransaction(message.MinerTransaction, true)) return;
             LocalNode.AllowHashes(context.TransactionHashes.Except(context.Transactions.Keys));
             if (context.Transactions.Count < context.TransactionHashes.Length)
                 localNode.SynchronizeMemoryPool();
@@ -348,7 +348,7 @@ private void SignAndRelay(ConsensusPayload payload)
             }
             wallet.Sign(sc);
             sc.Signable.Scripts = sc.GetScripts();
-            localNode.Relay(payload);
+            localNode.RelayDirectly(payload);
         }
 
         public void Start()
```

### src/AntShares/Core/ClaimTransaction.cs
```diff
@@ -84,7 +84,7 @@ public override bool Verify(IEnumerable<Transaction> mempool)
             if (!base.Verify(mempool)) return false;
             if (Claims.Length != Claims.Distinct().Count())
                 return false;
-            if (mempool.OfType<ClaimTransaction>().SelectMany(p => p.Claims).Intersect(Claims).Count() > 0)
+            if (mempool.OfType<ClaimTransaction>().Where(p => p != this).SelectMany(p => p.Claims).Intersect(Claims).Count() > 0)
                 return false;
             TransactionResult result = GetTransactionResults().FirstOrDefault(p => p.AssetId == Blockchain.AntCoin.Hash);
             if (result == null || result.Amount > Fixed8.Zero) return false;
```

### src/AntShares/Core/IssueTransaction.cs
```diff
@@ -60,7 +60,7 @@ public override bool Verify(IEnumerable<Transaction> mempool)
                 if (!Blockchain.Default.Ability.HasFlag(BlockchainAbility.Statistics))
                     return false;
                 Fixed8 quantity_issued = Blockchain.Default.GetQuantityIssued(r.AssetId);
-                quantity_issued += mempool.OfType<IssueTransaction>().SelectMany(p => p.Outputs).Where(p => p.AssetId == r.AssetId).Sum(p => p.Value);
+                quantity_issued += mempool.OfType<IssueTransaction>().Where(p => p != this).SelectMany(p => p.Outputs).Where(p => p.AssetId == r.AssetId).Sum(p => p.Value);
                 if (tx.Amount - quantity_issued < -r.Amount) return false;
             }
             return true;
```

### src/AntShares/Core/Transaction.cs
```diff
@@ -16,7 +16,7 @@ namespace AntShares.Core
     /// <summary>
     /// 一切交易的基类
     /// </summary>
-    public abstract class Transaction : IInventory
+    public abstract class Transaction : IEquatable<Transaction>, IInventory
     {
         /// <summary>
         /// 交易类型
@@ -318,14 +318,13 @@ bool IInventory.Verify()
         /// <returns>返回验证的结果</returns>
         public virtual bool Verify(IEnumerable<Transaction> mempool)
         {
-            if (Blockchain.Default.ContainsTransaction(Hash)) return true;
             if (!Blockchain.Default.Ability.HasFlag(BlockchainAbility.UnspentIndexes) || !Blockchain.Default.Ability.HasFlag(BlockchainAbility.TransactionIndexes))
                 return false;
             for (int i = 1; i < Inputs.Length; i++)
                 for (int j = 0; j < i; j++)
                     if (Inputs[i].PrevHash == Inputs[j].PrevHash && Inputs[i].PrevIndex == Inputs[j].PrevIndex)
                         return false;
-            if (mempool.SelectMany(p => p.Inputs).Intersect(Inputs).Count() > 0)
+            if (mempool.Where(p => p != this).SelectMany(p => p.Inputs).Intersect(Inputs).Count() > 0)
                 return false;
             if (Blockchain.Default.IsDoubleSpend(this))
                 return false;
```

### src/AntShares/Cryptography/Helper.cs
```diff
@@ -59,7 +59,7 @@ public static uint Murmur32(this IEnumerable<byte> value, uint seed)
         {
             using (Murmur3 murmur = new Murmur3(seed))
             {
-                return BitConverter.ToUInt32(murmur.ComputeHash(value.ToArray()), 0);
+                return murmur.ComputeHash(value.ToArray()).ToUInt32(0);
             }
         }
 
```

### src/AntShares/Cryptography/Murmur3.cs
```diff
@@ -31,7 +31,7 @@ protected override void HashCore(byte[] array, int ibStart, int cbSize)
             int alignedLength = ibStart + (cbSize - remainder);
             for (int i = ibStart; i < alignedLength; i += 4)
             {
-                uint k = ToUInt32(array, i);
+                uint k = array.ToUInt32(i);
                 k *= c1;
                 k = RotateLeft(k, r1);
                 k *= c2;
@@ -77,14 +77,5 @@ private static uint RotateLeft(uint x, byte n)
         {
             return (x << n) | (x >> (32 - n));
         }
-
-        [MethodImpl(MethodImplOptions.AggressiveInlining)]
-        unsafe private static uint ToUInt32(byte[] value, int startIndex)
-        {
-            fixed (byte* pbyte = &value[startIndex])
-            {
-                return *((uint*)pbyte);
-            }
-        }
     }
 }
```

### src/AntShares/Helper.cs
```diff
@@ -1,217 +1,263 @@
-﻿using System;
-using System.Collections.Generic;
-using System.Globalization;
-using System.Linq;
-using System.Numerics;
-using System.Security.Cryptography;
-using System.Text;
-
-namespace AntShares
-{
-    public static class Helper
-    {
-        private static readonly DateTime unixEpoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
-
-        private static int BitLen(int w)
-        {
-            return (w < 1 << 15 ? (w < 1 << 7
-                ? (w < 1 << 3 ? (w < 1 << 1
-                ? (w < 1 << 0 ? (w < 0 ? 32 : 0) : 1)
-                : (w < 1 << 2 ? 2 : 3)) : (w < 1 << 5
-                ? (w < 1 << 4 ? 4 : 5)
-                : (w < 1 << 6 ? 6 : 7)))
-                : (w < 1 << 11
-                ? (w < 1 << 9 ? (w < 1 << 8 ? 8 : 9) : (w < 1 << 10 ? 10 : 11))
-                : (w < 1 << 13 ? (w < 1 << 12 ? 12 : 13) : (w < 1 << 14 ? 14 : 15)))) : (w < 1 << 23 ? (w < 1 << 19
-                ? (w < 1 << 17 ? (w < 1 << 16 ? 16 : 17) : (w < 1 << 18 ? 18 : 19))
-                : (w < 1 << 21 ? (w < 1 << 20 ? 20 : 21) : (w < 1 << 22 ? 22 : 23))) : (w < 1 << 27
-                ? (w < 1 << 25 ? (w < 1 << 24 ? 24 : 25) : (w < 1 << 26 ? 26 : 27))
-                : (w < 1 << 29 ? (w < 1 << 28 ? 28 : 29) : (w < 1 << 30 ? 30 : 31)))));
-        }
-
-        internal static int GetBitLength(this BigInteger i)
-        {
-            byte[] b = i.ToByteArray();
-            return (b.Length - 1) * 8 + BitLen(i.Sign > 0 ? b[b.Length - 1] : 255 - b[b.Length - 1]);
-        }
-
-        internal static int GetLowestSetBit(this BigInteger i)
-        {
-            if (i.Sign == 0)
-                return -1;
-            byte[] b = i.ToByteArray();
-            int w = 0;
-            while (b[w] == 0)
-                w++;
-            for (int x = 0; x < 8; x++)
-                if ((b[w] & 1 << x) > 0)
-                    return x + w * 8;
-            throw new Exception();
-        }
-
-        public static byte[] HexToBytes(this string value)
-        {
-            if (value == null || value.Length == 0)
-                return new byte[0];
-            if (value.Length % 2 == 1)
-                throw new FormatException();
-            byte[] result = new byte[value.Length / 2];
-            for (int i = 0; i < result.Length; i++)
-                result[i] = byte.Parse(value.Substring(i * 2, 2), NumberStyles.AllowHexSpecifier);
-            return result;
-        }
-
-        internal static BigInteger Mod(this BigInteger x, BigInteger y)
-        {
-            x %= y;
-            if (x.Sign < 0)
-                x += y;
-            return x;
-        }
-
-        internal static BigInteger ModInverse(this BigInteger a, BigInteger n)
-        {
-            BigInteger i = n, v = 0, d = 1;
-            while (a > 0)
-            {
-                BigInteger t = i / a, x = a;
-                a = i % x;
-                i = x;
-                x = d;
-                d = v - t * x;
-                v = x;
-            }
-            v %= n;
-            if (v < 0) v = (v + n) % n;
-            return v;
-        }
-
-        internal static BigInteger NextBigInteger(this Random rand, int sizeInBits)
-        {
-            if (sizeInBits < 0)
-                throw new ArgumentException("sizeInBits must be non-negative");
-            if (sizeInBits == 0)
-                return 0;
-            byte[] b = new byte[sizeInBits / 8 + 1];
-            rand.NextBytes(b);
-            if (sizeInBits % 8 == 0)
-                b[b.Length - 1] = 0;
-            else
-                b[b.Length - 1] &= (byte)((1 << sizeInBits % 8) - 1);
-            return new BigInteger(b);
-        }
-
-        internal static BigInteger NextBigInteger(this RandomNumberGenerator rng, int sizeInBits)
-        {
-            if (sizeInBits < 0)
-                throw new ArgumentException("sizeInBits must be non-negative");
-            if (sizeInBits == 0)
-                return 0;
-            byte[] b = new byte[sizeInBits / 8 + 1];
-            rng.GetBytes(b);
-            if (sizeInBits % 8 == 0)
-                b[b.Length - 1] = 0;
-            else
-                b[b.Length - 1] &= (byte)((1 << sizeInBits % 8) - 1);
-            return new BigInteger(b);
-        }
-
-        public static Fixed8 Sum(this IEnumerable<Fixed8> source)
-        {
-            long sum = 0;
-            checked
-            {
-                foreach (Fixed8 item in source)
-                {
-                    sum += item.value;
-                }
-            }
-            return new Fixed8(sum);
-        }
-
-        public static Fixed8 Sum<TSource>(this IEnumerable<TSource> source, Func<TSource, Fixed8> selector)
-        {
-            return source.Select(selector).Sum();
-        }
-
-        internal static bool TestBit(this BigInteger i, int index)
-        {
-            return (i & (BigInteger.One << index)) > BigInteger.Zero;
-        }
-
-        public static DateTime ToDateTime(this uint timestamp)
-        {
-            return unixEpoch.AddSeconds(timestamp).ToLocalTime();
-        }
-
-        public static DateTime ToDateTime(this ulong timestamp)
-        {
-            return unixEpoch.AddSeconds(timestamp).ToLocalTime();
-        }
-
-        public static string ToHexString(this IEnumerable<byte> value)
-        {
-            StringBuilder sb = new StringBuilder();
-            foreach (byte b in value)
-                sb.AppendFormat("{0:x2}", b);
-            return sb.ToString();
-        }
-
-        public static uint ToTimestamp(this DateTime time)
-        {
-            return (uint)(time.ToUniversalTime() - unixEpoch).TotalSeconds;
-        }
-
-        internal static long WeightedAverage<T>(this IEnumerable<T> source, Func<T, long> valueSelector, Func<T, long> weightSelector)
-        {
-            long sum_weight = 0;
-            long sum_value = 0;
-            foreach (T item in source)
-            {
-                long weight = weightSelector(item);
-                sum_weight += weight;
-                sum_value += valueSelector(item) * weight;
-            }
-            if (sum_value == 0) return 0;
-            return sum_value / sum_weight;
-        }
-
-        internal static IEnumerable<TResult> WeightedFilter<T, TResult>(this IList<T> source, double start, double end, Func<T, long> weightSelector, Func<T, long, TResult> resultSelector)
-        {
-            if (source == null) throw new ArgumentNullException(nameof(source));
-            if (start < 0 || start > 1) throw new ArgumentOutOfRangeException(nameof(start));
-            if (end < start || start + end > 1) throw new ArgumentOutOfRangeException(nameof(end));
-            if (weightSelector == null) throw new ArgumentNullException(nameof(weightSelector));
-            if (resultSelector == null) throw new ArgumentNullException(nameof(resultSelector));
-            if (source.Count == 0 || start == end) yield break;
-            double amount = source.Sum(weightSelector);
-            long sum = 0;
-            double current = 0;
-            foreach (T item in source)
-            {
-                if (current >= end) break;
-                long weight = weightSelector(item);
-                sum += weight;
-                double old = current;
-                current = sum / amount;
-                if (current <= start) continue;
-                if (old < start)
-                {
-                    if (current > end)
-                    {
-                        weight = (long)((end - start) * amount);
-                    }
-                    else
-                    {
-                        weight = (long)((current - start) * amount);
-                    }
-                }
-                else if (current > end)
-                {
-                    weight = (long)((end - old) * amount);
-                }
-                yield return resultSelector(item, weight);
-            }
-        }
-    }
-}
+﻿using System;
+using System.Collections.Generic;
+using System.Globalization;
+using System.Linq;
+using System.Numerics;
+using System.Runtime.CompilerServices;
+using System.Security.Cryptography;
+using System.Text;
+
+namespace AntShares
+{
+    public static class Helper
+    {
+        private static readonly DateTime unixEpoch = new DateTime(1970, 1, 1, 0, 0, 0, DateTimeKind.Utc);
+
+        private static int BitLen(int w)
+        {
+            return (w < 1 << 15 ? (w < 1 << 7
+                ? (w < 1 << 3 ? (w < 1 << 1
+                ? (w < 1 << 0 ? (w < 0 ? 32 : 0) : 1)
+                : (w < 1 << 2 ? 2 : 3)) : (w < 1 << 5
+                ? (w < 1 << 4 ? 4 : 5)
+                : (w < 1 << 6 ? 6 : 7)))
+                : (w < 1 << 11
+                ? (w < 1 << 9 ? (w < 1 << 8 ? 8 : 9) : (w < 1 << 10 ? 10 : 11))
+                : (w < 1 << 13 ? (w < 1 << 12 ? 12 : 13) : (w < 1 << 14 ? 14 : 15)))) : (w < 1 << 23 ? (w < 1 << 19
+                ? (w < 1 << 17 ? (w < 1 << 16 ? 16 : 17) : (w < 1 << 18 ? 18 : 19))
+                : (w < 1 << 21 ? (w < 1 << 20 ? 20 : 21) : (w < 1 << 22 ? 22 : 23))) : (w < 1 << 27
+                ? (w < 1 << 25 ? (w < 1 << 24 ? 24 : 25) : (w < 1 << 26 ? 26 : 27))
+                : (w < 1 << 29 ? (w < 1 << 28 ? 28 : 29) : (w < 1 << 30 ? 30 : 31)))));
+        }
+
+        internal static int GetBitLength(this BigInteger i)
+        {
+            byte[] b = i.ToByteArray();
+            return (b.Length - 1) * 8 + BitLen(i.Sign > 0 ? b[b.Length - 1] : 255 - b[b.Length - 1]);
+        }
+
+        internal static int GetLowestSetBit(this BigInteger i)
+        {
+            if (i.Sign == 0)
+                return -1;
+            byte[] b = i.ToByteArray();
+            int w = 0;
+            while (b[w] == 0)
+                w++;
+            for (int x = 0; x < 8; x++)
+                if ((b[w] & 1 << x) > 0)
+                    return x + w * 8;
+            throw new Exception();
+        }
+
+        public static byte[] HexToBytes(this string value)
+        {
+            if (value == null || value.Length == 0)
+                return new byte[0];
+            if (value.Length % 2 == 1)
+                throw new FormatException();
+            byte[] result = new byte[value.Length / 2];
+            for (int i = 0; i < result.Length; i++)
+                result[i] = byte.Parse(value.Substring(i * 2, 2), NumberStyles.AllowHexSpecifier);
+            return result;
+        }
+
+        internal static BigInteger Mod(this BigInteger x, BigInteger y)
+        {
+            x %= y;
+            if (x.Sign < 0)
+                x += y;
+            return x;
+        }
+
+        internal static BigInteger ModInverse(this BigInteger a, BigInteger n)
+        {
+            BigInteger i = n, v = 0, d = 1;
+            while (a > 0)
+            {
+                BigInteger t = i / a, x = a;
+                a = i % x;
+                i = x;
+                x = d;
+                d = v - t * x;
+                v = x;
+            }
+            v %= n;
+            if (v < 0) v = (v + n) % n;
+            return v;
+        }
+
+        internal static BigInteger NextBigInteger(this Random rand, int sizeInBits)
+        {
+            if (sizeInBits < 0)
+                throw new ArgumentException("sizeInBits must be non-negative");
+            if (sizeInBits == 0)
+                return 0;
+            byte[] b = new byte[sizeInBits / 8 + 1];
+            rand.NextBytes(b);
+            if (sizeInBits % 8 == 0)
+                b[b.Length - 1] = 0;
+            else
+                b[b.Length - 1] &= (byte)((1 << sizeInBits % 8) - 1);
+            return new BigInteger(b);
+        }
+
+        internal static BigInteger NextBigInteger(this RandomNumberGenerator rng, int sizeInBits)
+        {
+            if (sizeInBits < 0)
+                throw new ArgumentException("sizeInBits must be non-negative");
+            if (sizeInBits == 0)
+                return 0;
+            byte[] b = new byte[sizeInBits / 8 + 1];
+            rng.GetBytes(b);
+            if (sizeInBits % 8 == 0)
+                b[b.Length - 1] = 0;
+            else
+                b[b.Length - 1] &= (byte)((1 << sizeInBits % 8) - 1);
+            return new BigInteger(b);
+        }
+
+        public static Fixed8 Sum(this IEnumerable<Fixed8> source)
+        {
+            long sum = 0;
+            checked
+            {
+                foreach (Fixed8 item in source)
+                {
+                    sum += item.value;
+                }
+            }
+            return new Fixed8(sum);
+        }
+
+        public static Fixed8 Sum<TSource>(this IEnumerable<TSource> source, Func<TSource, Fixed8> selector)
+        {
+            return source.Select(selector).Sum();
+        }
+
+        internal static bool TestBit(this BigInteger i, int index)
+        {
+            return (i & (BigInteger.One << index)) > BigInteger.Zero;
+        }
+
+        public static DateTime ToDateTime(this uint timestamp)
+        {
+            return unixEpoch.AddSeconds(timestamp).ToLocalTime();
+        }
+
+        public static DateTime ToDateTime(this ulong timestamp)
+        {
+            return unixEpoch.AddSeconds(timestamp).ToLocalTime();
+        }
+
+        public static string ToHexString(this IEnumerable<byte> value)
+        {
+            StringBuilder sb = new StringBuilder();
+            foreach (byte b in value)
+                sb.AppendFormat("{0:x2}", b);
+            return sb.ToString();
+        }
+
+        [MethodImpl(MethodImplOptions.AggressiveInlining)]
+        unsafe internal static int ToInt32(this byte[] value, int startIndex)
+        {
+            fixed (byte* pbyte = &value[startIndex])
+            {
+                return *((int*)pbyte);
+            }
+        }
+
+        [MethodImpl(MethodImplOptions.AggressiveInlining)]
+        unsafe internal static long ToInt64(this byte[] value, int startIndex)
+        {
+            fixed (byte* pbyte = &value[startIndex])
+            {
+                return *((long*)pbyte);
+            }
+        }
+
+        public static uint ToTimestamp(this DateTime time)
+        {
+            return (uint)(time.ToUniversalTime() - unixEpoch).TotalSeconds;
+        }
+
+        [MethodImpl(MethodImplOptions.AggressiveInlining)]
+        unsafe internal static ushort ToUInt16(this byte[] value, int startIndex)
+        {
+            fixed (byte* pbyte = &value[startIndex])
+            {
+                return *((ushort*)pbyte);
+            }
+        }
+
+        [MethodImpl(MethodImplOptions.AggressiveInlining)]
+        unsafe internal static uint ToUInt32(this byte[] value, int startIndex)
+        {
+            fixed (byte* pbyte = &value[startIndex])
+            {
+                return *((uint*)pbyte);
+            }
+        }
+
+        [MethodImpl(MethodImplOptions.AggressiveInlining)]
+        unsafe internal static ulong ToUInt64(this byte[] value, int startIndex)
+        {
+            fixed (byte* pbyte = &value[startIndex])
+            {
+                return *((ulong*)pbyte);
+            }
+        }
+
+        internal static long WeightedAverage<T>(this IEnumerable<T> source, Func<T, long> valueSelector, Func<T, long> weightSelector)
+        {
+            long sum_weight = 0;
+            long sum_value = 0;
+            foreach (T item in source)
+            {
+                long weight = weightSelector(item);
+                sum_weight += weight;
+                sum_value += valueSelector(item) * weight;
+            }
+            if (sum_value == 0) return 0;
+            return sum_value / sum_weight;
+        }
+
+        internal static IEnumerable<TResult> WeightedFilter<T, TResult>(this IList<T> source, double start, double end, Func<T, long> weightSelector, Func<T, long, TResult> resultSelector)
+        {
+            if (source == null) throw new ArgumentNullException(nameof(source));
+            if (start < 0 || start > 1) throw new ArgumentOutOfRangeException(nameof(start));
+            if (end < start || start + end > 1) throw new ArgumentOutOfRangeException(nameof(end));
+            if (weightSelector == null) throw new ArgumentNullException(nameof(weightSelector));
+            if (resultSelector == null) throw new ArgumentNullException(nameof(resultSelector));
+            if (source.Count == 0 || start == end) yield break;
+            double amount = source.Sum(weightSelector);
+            long sum = 0;
+            double current = 0;
+            foreach (T item in source)
+            {
+                if (current >= end) break;
+                long weight = weightSelector(item);
+                sum += weight;
+                double old = current;
+                current = sum / amount;
+                if (current <= start) continue;
+                if (old < start)
+                {
+                    if (current > end)
+                    {
+                        weight = (long)((end - start) * amount);
+                    }
+                    else
+                    {
+                        weight = (long)((current - start) * amount);
+                    }
+                }
+                else if (current > end)
+                {
+                    weight = (long)((end - old) * amount);
+                }
+                yield return resultSelector(item, weight);
+            }
+        }
+    }
+}
```

### src/AntShares/Implementations/Blockchains/LevelDB/LevelDBBlockchain.cs
```diff
@@ -40,12 +40,12 @@ public LevelDBBlockchain(string path)
                 ReadOptions options = new ReadOptions { FillCache = false };
                 value = db.Get(options, SliceBuilder.Begin(DataEntryPrefix.SYS_CurrentBlock));
                 UInt256 current_header_hash = new UInt256(value.ToArray().Take(32).ToArray());
-                this.current_block_height = BitConverter.ToUInt32(value.ToArray(), 32);
+                this.current_block_height = value.ToArray().ToUInt32(32);
                 uint current_header_height = current_block_height;
                 if (db.TryGet(options, SliceBuilder.Begin(DataEntryPrefix.SYS_CurrentHeader), out value))
                 {
                     current_header_hash = new UInt256(value.ToArray().Take(32).ToArray());
-                    current_header_height = BitConverter.ToUInt32(value.ToArray(), 32);
+                    current_header_height = value.ToArray().ToUInt32(32);
                 }
                 foreach (UInt256 hash in db.Find(options, SliceBuilder.Begin(DataEntryPrefix.IX_HeaderHashList), (k, v) =>
                 {
@@ -54,7 +54,7 @@ public LevelDBBlockchain(string path)
                     {
                         return new
                         {
-                            Index = BitConverter.ToUInt32(k.ToArray(), 1),
+                            Index = k.ToArray().ToUInt32(1),
                             Hashes = r.ReadSerializableArray<UInt256>()
                         };
                     }
@@ -304,7 +304,7 @@ public override long GetSysFeeAmount(UInt256 hash)
             Slice value;
             if (!db.TryGet(ReadOptions.Default, SliceBuilder.Begin(DataEntryPrefix.DATA_Header).Add(hash), out value))
                 return 0;
-            return BitConverter.ToInt64(value.ToArray(), 0);
+            return value.ToArray().ToInt64(0);
         }
 
         public override Transaction GetTransaction(UInt256 hash, out int height)
@@ -323,7 +323,7 @@ private Transaction GetTransaction(ReadOptions options, UInt256 hash, out int he
             if (db.TryGet(options, SliceBuilder.Begin(DataEntryPrefix.DATA_Transaction).Add(hash), out value))
             {
                 byte[] data = value.ToArray();
-                height = BitConverter.ToInt32(data, 0);
+                height = data.ToInt32(0);
                 return Transaction.DeserializeFrom(data, sizeof(uint));
             }
             else
@@ -343,11 +343,11 @@ public override Dictionary<ushort, Claimable> GetUnclaimed(UInt256 hash)
             {
                 const int UnclaimedItemSize = sizeof(ushort) + sizeof(uint);
                 byte[] data = value.ToArray();
-                return Enumerable.Range(0, data.Length / UnclaimedItemSize).ToDictionary(i => BitConverter.ToUInt16(data, i * UnclaimedItemSize), i => new Claimable
+                return Enumerable.Range(0, data.Length / UnclaimedItemSize).ToDictionary(i => data.ToUInt16(i * UnclaimedItemSize), i => new Claimable
                 {
-                    Output = tx.Outputs[BitConverter.ToUInt16(data, i * UnclaimedItemSize)],
+                    Output = tx.Outputs[data.ToUInt16(i * UnclaimedItemSize)],
                     StartHeight = (uint)height,
-                    EndHeight = BitConverter.ToUInt32(data, i * UnclaimedItemSize + sizeof(ushort))
+                    EndHeight = data.ToUInt32(i * UnclaimedItemSize + sizeof(ushort))
                 });
             }
             else
@@ -455,7 +455,7 @@ private void Persist(Block block)
                 if (!db.TryGet(ReadOptions.Default, SliceBuilder.Begin(DataEntryPrefix.IX_Unclaimed).Add(p), out value))
                     value = new byte[0];
                 byte[] data = value.ToArray();
-                return Enumerable.Range(0, data.Length / UnclaimedItemSize).ToDictionary(i => BitConverter.ToUInt16(data, i * UnclaimedItemSize), i => BitConverter.ToUInt32(data, i * UnclaimedItemSize + sizeof(ushort)));
+                return Enumerable.Range(0, data.Length / UnclaimedItemSize).ToDictionary(i => data.ToUInt16(i * UnclaimedItemSize), i => data.ToUInt32(i * UnclaimedItemSize + sizeof(ushort)));
             });
             MultiValueDictionary<UInt256, ushort> unspent_votes = new MultiValueDictionary<UInt256, ushort>(p =>
             {
```

### src/AntShares/Implementations/Blockchains/LevelDB/Slice.cs
```diff
@@ -1,217 +1,244 @@
-﻿using AntShares.Cryptography;
-using System;
-using System.Linq;
-using System.Runtime.InteropServices;
-using System.Text;
-
-namespace AntShares.Implementations.Blockchains.LevelDB
-{
-    internal struct Slice : IComparable<Slice>, IEquatable<Slice>
-    {
-        internal byte[] buffer;
-
-        internal Slice(IntPtr data, UIntPtr length)
-        {
-            buffer = new byte[(int)length];
-            Marshal.Copy(data, buffer, 0, (int)length);
-        }
-
-        public int CompareTo(Slice other)
-        {
-            for (int i = 0; i < buffer.Length && i < other.buffer.Length; i++)
-            {
-                int r = buffer[i].CompareTo(other.buffer[i]);
-                if (r != 0) return r;
-            }
-            return buffer.Length.CompareTo(other.buffer.Length);
-        }
-
-        public bool Equals(Slice other)
-        {
-            if (buffer.Length != other.buffer.Length) return false;
-            return buffer.SequenceEqual(other.buffer);
-        }
-
-        public override bool Equals(object obj)
-        {
-            if (ReferenceEquals(null, obj)) return false;
-            if (!(obj is Slice)) return false;
-            return Equals((Slice)obj);
-        }
-
-        public override int GetHashCode()
-        {
-            return BitConverter.ToInt32(buffer.Sha256(), 0);
-        }
-
-        public byte[] ToArray()
-        {
-            return buffer ?? new byte[0];
-        }
-
-        public bool ToBoolean()
-        {
-            if (buffer.Length != sizeof(bool))
-                throw new InvalidCastException();
-            return BitConverter.ToBoolean(buffer, 0);
-        }
-
-        public byte ToByte()
-        {
-            if (buffer.Length != sizeof(byte))
-                throw new InvalidCastException();
-            return buffer[0];
-        }
-
-        public double ToDouble()
-        {
-            if (buffer.Length != sizeof(double))
-                throw new InvalidCastException();
-            return BitConverter.ToDouble(buffer, 0);
-        }
-
-        public short ToInt16()
-        {
-            if (buffer.Length != sizeof(short))
-                throw new InvalidCastException();
-            return BitConverter.ToInt16(buffer, 0);
-        }
-
-        public int ToInt32()
-        {
-            if (buffer.Length != sizeof(int))
-                throw new InvalidCastException();
-            return BitConverter.ToInt32(buffer, 0);
-        }
-
-        public long ToInt64()
-        {
-            if (buffer.Length != sizeof(long))
-                throw new InvalidCastException();
-            return BitConverter.ToInt64(buffer, 0);
-        }
-
-        public float ToSingle()
-        {
-            if (buffer.Length != sizeof(float))
-                throw new InvalidCastException();
-            return BitConverter.ToSingle(buffer, 0);
-        }
-
-        public override string ToString()
-        {
-            return Encoding.UTF8.GetString(buffer);
-        }
-
-        public ushort ToUInt16()
-        {
-            if (buffer.Length != sizeof(ushort))
-                throw new InvalidCastException();
-            return BitConverter.ToUInt16(buffer, 0);
-        }
-
-        public uint ToUInt32()
-        {
-            if (buffer.Length != sizeof(uint))
-                throw new InvalidCastException();
-            return BitConverter.ToUInt32(buffer, 0);
-        }
-
-        public ulong ToUInt64()
-        {
-            if (buffer.Length != sizeof(ulong))
-                throw new InvalidCastException();
-            return BitConverter.ToUInt64(buffer, 0);
-        }
-
-        public static implicit operator Slice(byte[] data)
-        {
-            return new Slice { buffer = data };
-        }
-
-        public static implicit operator Slice(bool data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(byte data)
-        {
-            return new Slice { buffer = new[] { data } };
-        }
-
-        public static implicit operator Slice(double data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(short data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(int data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(long data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(float data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(string data)
-        {
-            return new Slice { buffer = Encoding.UTF8.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(ushort data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(uint data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static implicit operator Slice(ulong data)
-        {
-            return new Slice { buffer = BitConverter.GetBytes(data) };
-        }
-
-        public static bool operator <(Slice x, Slice y)
-        {
-            return x.CompareTo(y) < 0;
-        }
-
-        public static bool operator <=(Slice x, Slice y)
-        {
-            return x.CompareTo(y) <= 0;
-        }
-
-        public static bool operator >(Slice x, Slice y)
-        {
-            return x.CompareTo(y) > 0;
-        }
-
-        public static bool operator >=(Slice x, Slice y)
-        {
-            return x.CompareTo(y) >= 0;
-        }
-
-        public static bool operator ==(Slice x, Slice y)
-        {
-            return x.Equals(y);
-        }
-
-        public static bool operator !=(Slice x, Slice y)
-        {
-            return !x.Equals(y);
-        }
-    }
-}
+﻿using AntShares.Cryptography;
+using System;
+using System.Linq;
+using System.Runtime.InteropServices;
+using System.Text;
+
+namespace AntShares.Implementations.Blockchains.LevelDB
+{
+    internal struct Slice : IComparable<Slice>, IEquatable<Slice>
+    {
+        internal byte[] buffer;
+
+        internal Slice(IntPtr data, UIntPtr length)
+        {
+            buffer = new byte[(int)length];
+            Marshal.Copy(data, buffer, 0, (int)length);
+        }
+
+        public int CompareTo(Slice other)
+        {
+            for (int i = 0; i < buffer.Length && i < other.buffer.Length; i++)
+            {
+                int r = buffer[i].CompareTo(other.buffer[i]);
+                if (r != 0) return r;
+            }
+            return buffer.Length.CompareTo(other.buffer.Length);
+        }
+
+        public bool Equals(Slice other)
+        {
+            if (buffer.Length != other.buffer.Length) return false;
+            return buffer.SequenceEqual(other.buffer);
+        }
+
+        public override bool Equals(object obj)
+        {
+            if (ReferenceEquals(null, obj)) return false;
+            if (!(obj is Slice)) return false;
+            return Equals((Slice)obj);
+        }
+
+        public override int GetHashCode()
+        {
+            return buffer.Sha256().ToInt32(0);
+        }
+
+        public byte[] ToArray()
+        {
+            return buffer ?? new byte[0];
+        }
+
+        unsafe public bool ToBoolean()
+        {
+            if (buffer.Length != sizeof(bool))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((bool*)pbyte);
+            }
+        }
+
+        public byte ToByte()
+        {
+            if (buffer.Length != sizeof(byte))
+                throw new InvalidCastException();
+            return buffer[0];
+        }
+
+        unsafe public double ToDouble()
+        {
+            if (buffer.Length != sizeof(double))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((double*)pbyte);
+            }
+        }
+
+        unsafe public short ToInt16()
+        {
+            if (buffer.Length != sizeof(short))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((short*)pbyte);
+            }
+        }
+
+        unsafe public int ToInt32()
+        {
+            if (buffer.Length != sizeof(int))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((int*)pbyte);
+            }
+        }
+
+        unsafe public long ToInt64()
+        {
+            if (buffer.Length != sizeof(long))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((long*)pbyte);
+            }
+        }
+
+        unsafe public float ToSingle()
+        {
+            if (buffer.Length != sizeof(float))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((float*)pbyte);
+            }
+        }
+
+        public override string ToString()
+        {
+            return Encoding.UTF8.GetString(buffer);
+        }
+
+        unsafe public ushort ToUInt16()
+        {
+            if (buffer.Length != sizeof(ushort))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((ushort*)pbyte);
+            }
+        }
+
+        unsafe public uint ToUInt32()
+        {
+            if (buffer.Length != sizeof(uint))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((uint*)pbyte);
+            }
+        }
+
+        unsafe public ulong ToUInt64()
+        {
+            if (buffer.Length != sizeof(ulong))
+                throw new InvalidCastException();
+            fixed (byte* pbyte = &buffer[0])
+            {
+                return *((ulong*)pbyte);
+            }
+        }
+
+        public static implicit operator Slice(byte[] data)
+        {
+            return new Slice { buffer = data };
+        }
+
+        public static implicit operator Slice(bool data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(byte data)
+        {
+            return new Slice { buffer = new[] { data } };
+        }
+
+        public static implicit operator Slice(double data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(short data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(int data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(long data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(float data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(string data)
+        {
+            return new Slice { buffer = Encoding.UTF8.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(ushort data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(uint data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static implicit operator Slice(ulong data)
+        {
+            return new Slice { buffer = BitConverter.GetBytes(data) };
+        }
+
+        public static bool operator <(Slice x, Slice y)
+        {
+            return x.CompareTo(y) < 0;
+        }
+
+        public static bool operator <=(Slice x, Slice y)
+        {
+            return x.CompareTo(y) <= 0;
+        }
+
+        public static bool operator >(Slice x, Slice y)
+        {
+            return x.CompareTo(y) > 0;
+        }
+
+        public static bool operator >=(Slice x, Slice y)
+        {
+            return x.CompareTo(y) >= 0;
+        }
+
+        public static bool operator ==(Slice x, Slice y)
+        {
+            return x.Equals(y);
+        }
+
+        public static bool operator !=(Slice x, Slice y)
+        {
+            return !x.Equals(y);
+        }
+    }
+}
```

### src/AntShares/Implementations/Wallets/EntityFramework/UserWallet.cs
```diff
@@ -186,10 +186,10 @@ public static Version GetVersion(string path)
                 buffer = ctx.Keys.FirstOrDefault(p => p.Name == "Version")?.Value;
             }
             if (buffer == null) return new Version(0, 0);
-            int major = BitConverter.ToInt32(buffer, 0);
-            int minor = BitConverter.ToInt32(buffer, 4);
-            int build = BitConverter.ToInt32(buffer, 8);
-            int revision = BitConverter.ToInt32(buffer, 12);
+            int major = buffer.ToInt32(0);
+            int minor = buffer.ToInt32(4);
+            int build = buffer.ToInt32(8);
+            int revision = buffer.ToInt32(12);
             return new Version(major, minor, build, revision);
         }
 
@@ -279,7 +279,7 @@ public static void Migrate(string path_old, string path_new)
                 ctx_new.Addresses.AddRange(ctx_old.Contracts.Select(p => new Address { ScriptHash = p.ScriptHash }));
                 ctx_new.Contracts.AddRange(ctx_old.Contracts);
                 ctx_new.Keys.AddRange(ctx_old.Keys.Where(p => p.Name != "Height" && p.Name != "Version"));
-                SaveStoredData(ctx_new, "Height", BitConverter.GetBytes(0));
+                SaveStoredData(ctx_new, "Height", new byte[sizeof(int)]);
                 SaveStoredData(ctx_new, "Version", new[] { current_version.Major, current_version.Minor, current_version.Build, current_version.Revision }.Select(p => BitConverter.GetBytes(p)).SelectMany(p => p).ToArray());
                 ctx_new.SaveChanges();
             }
```

### src/AntShares/Network/AddingTransactionEventArgs.cs
```diff
@@ -1,15 +0,0 @@
-﻿using AntShares.Core;
-using System.ComponentModel;
-
-namespace AntShares.Network
-{
-    public class AddingTransactionEventArgs : CancelEventArgs
-    {
-        public Transaction Transaction { get; private set; }
-
-        public AddingTransactionEventArgs(Transaction tx)
-        {
-            Transaction = tx;
-        }
-    }
-}
```

### src/AntShares/Network/LocalNode.cs
```diff
@@ -1,304 +1,340 @@
-﻿using AntShares.Core;
-using AntShares.IO;
-using AntShares.IO.Caching;
-using System;
-using System.Collections.Generic;
-using System.IO;
-using System.Linq;
-using System.Net;
-using System.Net.NetworkInformation;
-using System.Net.Sockets;
-using System.Reflection;
-using System.Text;
-using System.Threading;
-using System.Threading.Tasks;
-
-namespace AntShares.Network
-{
-    public class LocalNode : IDisposable
-    {
-        public static event EventHandler<AddingTransactionEventArgs> AddingTransaction;
-        public static event EventHandler<IInventory> NewInventory;
-
-        public const uint PROTOCOL_VERSION = 0;
-        private const int CONNECTED_MAX = 10;
-        private const int UNCONNECTED_MAX = 1000;
-
-        private static readonly Dictionary<UInt256, Transaction> MemoryPool = new Dictionary<UInt256, Transaction>();
-        internal static readonly HashSet<UInt256> KnownHashes = new HashSet<UInt256>();
-        internal readonly RelayCache RelayCache = new RelayCache(100);
-
-        private static readonly HashSet<IPEndPoint> unconnectedPeers = new HashSet<IPEndPoint>();
-        private static readonly HashSet<IPEndPoint> badPeers = new HashSet<IPEndPoint>();
-        internal readonly List<RemoteNode> connectedPeers = new List<RemoteNode>();
-
-        internal static readonly HashSet<IPAddress> LocalAddresses = new HashSet<IPAddress>();
-        internal ushort Port;
-        internal readonly uint Nonce;
-        private TcpListener listener;
-        private Thread connectThread;
-        private int started = 0;
-        private int disposed = 0;
-
-        public bool GlobalMissionsEnabled { get; set; } = true;
-        public int RemoteNodeCount => connectedPeers.Count;
-        public bool ServiceEnabled { get; set; } = true;
-        public bool UpnpEnabled { get; set; } = false;
-        public string UserAgent { get; set; }
-
-        static LocalNode()
-        {
-            LocalAddresses.UnionWith(NetworkInterface.GetAllNetworkInterfaces().SelectMany(p => p.GetIPProperties().UnicastAddresses).Select(p => p.Address.MapToIPv6()));
-            Blockchain.PersistCompleted += Blockchain_PersistCompleted;
-        }
-
-        public LocalNode()
-        {
-            Random rand = new Random();
-            this.Nonce = (uint)rand.Next();
-            this.connectThread = new Thread(ConnectToPeersLoop)
-            {
-                IsBackground = true,
-                Name = "LocalNode.ConnectToPeersLoop"
-            };
-            this.UserAgent = string.Format("/AntSharesCore:{0}/", GetType().GetTypeInfo().Assembly.GetName().Version.ToString(3));
-        }
-
-        private async Task AcceptPeersAsync()
-        {
-            while (disposed == 0)
-            {
-                Socket socket;
-                try
-                {
-                    socket = await listener.AcceptSocketAsync();
-                }
-                catch (ObjectDisposedException)
-                {
-                    break;
-                }
-                catch (SocketException)
-                {
-                    break;
-                }
-                TcpRemoteNode remoteNode = new TcpRemoteNode(this, socket);
+﻿using AntShares.Core;
+using AntShares.IO;
+using AntShares.IO.Caching;
+using System;
+using System.Collections.Concurrent;
+using System.Collections.Generic;
+using System.IO;
+using System.Linq;
+using System.Net;
+using System.Net.NetworkInformation;
+using System.Net.Sockets;
+using System.Reflection;
+using System.Text;
+using System.Threading;
+using System.Threading.Tasks;
+
+namespace AntShares.Network
+{
+    public class LocalNode : IDisposable
+    {
+        public static event EventHandler<IInventory> NewInventory;
+
+        public const uint PROTOCOL_VERSION = 0;
+        private const int CONNECTED_MAX = 10;
+        private const int UNCONNECTED_MAX = 1000;
+
+        private static readonly Dictionary<UInt256, Transaction> mem_pool = new Dictionary<UInt256, Transaction>();
+        private readonly HashSet<Transaction> temp_pool = new HashSet<Transaction>();
+        internal static readonly HashSet<UInt256> KnownHashes = new HashSet<UInt256>();
+        internal readonly RelayCache RelayCache = new RelayCache(100);
+
+        private static readonly HashSet<IPEndPoint> unconnectedPeers = new HashSet<IPEndPoint>();
+        private static readonly HashSet<IPEndPoint> badPeers = new HashSet<IPEndPoint>();
+        internal readonly List<RemoteNode> connectedPeers = new List<RemoteNode>();
+
+        internal static readonly HashSet<IPAddress> LocalAddresses = new HashSet<IPAddress>();
+        internal ushort Port;
+        internal readonly uint Nonce;
+        private TcpListener listener;
+        private Thread connectThread;
+        private Thread poolThread;
+        private readonly AutoResetEvent new_tx_event = new AutoResetEvent(false);
+        private int started = 0;
+        private int disposed = 0;
+
+        public bool GlobalMissionsEnabled { get; set; } = true;
+        public int RemoteNodeCount => connectedPeers.Count;
+        public bool ServiceEnabled { get; set; } = true;
+        public bool UpnpEnabled { get; set; } = false;
+        public string UserAgent { get; set; }
+
+        static LocalNode()
+        {
+            LocalAddresses.UnionWith(NetworkInterface.GetAllNetworkInterfaces().SelectMany(p => p.GetIPProperties().UnicastAddresses).Select(p => p.Address.MapToIPv6()));
+            Blockchain.PersistCompleted += Blockchain_PersistCompleted;
+        }
+
+        public LocalNode()
+        {
+            Random rand = new Random();
+            this.Nonce = (uint)rand.Next();
+            this.connectThread = new Thread(ConnectToPeersLoop)
+            {
+                IsBackground = true,
+                Name = "LocalNode.ConnectToPeersLoop"
+            };
+            if (Blockchain.Default != null)
+            {
+                this.poolThread = new Thread(AddTransactionLoop)
+                {
+                    IsBackground = true,
+                    Name = "LocalNode.AddTransactionLoop"
+                };
+            }
+            this.UserAgent = string.Format("/AntSharesCore:{0}/", GetType().GetTypeInfo().Assembly.GetName().Version.ToString(3));
+        }
+
+        private async Task AcceptPeersAsync()
+        {
+            while (disposed == 0)
+            {
+                Socket socket;
+                try
+                {
+                    socket = await listener.AcceptSocketAsync();
+                }
+                catch (ObjectDisposedException)
+                {
+                    break;
+                }
+                catch (SocketException)
+                {
+                    break;
+                }
+                TcpRemoteNode remoteNode = new TcpRemoteNode(this, socket);
                 OnConnected(remoteNode);
-            }
-        }
-
-        private bool AddTransaction(Transaction tx)
-        {
-            if (Blockchain.Default == null) return false;
-            lock (MemoryPool)
-            {
-                if (MemoryPool.ContainsKey(tx.Hash)) return false;
-                if (Blockchain.Default.ContainsTransaction(tx.Hash)) return false;
-                if (!tx.Verify(MemoryPool.Values)) return false;
-                AddingTransactionEventArgs args = new AddingTransactionEventArgs(tx);
-                AddingTransaction?.Invoke(this, args);
-                if (!args.Cancel) MemoryPool.Add(tx.Hash, tx);
-                return !args.Cancel;
-            }
-        }
-
-        public static void AllowHashes(IEnumerable<UInt256> hashes)
-        {
-            lock (KnownHashes)
-            {
-                KnownHashes.ExceptWith(hashes);
-            }
-        }
-
-        private static void Blockchain_PersistCompleted(object sender, Block block)
-        {
-            HashSet<CoinReference> inputs = new HashSet<CoinReference>(block.Transactions.SelectMany(p => p.Inputs));
-            lock (MemoryPool)
-            {
-                foreach (Transaction tx in block.Transactions)
-                {
-                    MemoryPool.Remove(tx.Hash);
-                }
-                foreach (Transaction tx in MemoryPool.Values.ToArray())
-                {
-                    foreach (CoinReference input in tx.Inputs)
-                        if (inputs.Contains(input))
-                        {
-                            MemoryPool.Remove(tx.Hash);
-                            break;
-                        }
-                }
-            }
-        }
-
-        public async Task ConnectToPeerAsync(string hostNameOrAddress, int port)
-        {
-            IPAddress ipAddress;
-            if (IPAddress.TryParse(hostNameOrAddress, out ipAddress))
-            {
-                ipAddress = ipAddress.MapToIPv6();
-            }
-            else
-            {
-                IPHostEntry entry;
-                try
-                {
-                    entry = await Dns.GetHostEntryAsync(hostNameOrAddress);
-                }
-                catch (SocketException)
-                {
-                    return;
-                }
-                ipAddress = entry.AddressList.FirstOrDefault(p => p.AddressFamily == AddressFamily.InterNetwork || p.IsIPv6Teredo)?.MapToIPv6();
-                if (ipAddress == null) return;
-            }
-            await ConnectToPeerAsync(new IPEndPoint(ipAddress, port));
-        }
-
-        public async Task ConnectToPeerAsync(IPEndPoint remoteEndpoint)
-        {
-            if (remoteEndpoint.Port == Port && LocalAddresses.Contains(remoteEndpoint.Address)) return;
-            lock (unconnectedPeers)
-            {
-                unconnectedPeers.Remove(remoteEndpoint);
+            }
+        }
+
+        private static bool AddTransaction(Transaction tx)
+        {
+            if (Blockchain.Default == null) return false;
+            lock (mem_pool)
+            {
+                if (mem_pool.ContainsKey(tx.Hash)) return false;
+                if (Blockchain.Default.ContainsTransaction(tx.Hash)) return false;
+                if (!tx.Verify(mem_pool.Values)) return false;
+                mem_pool.Add(tx.Hash, tx);
+            }
+            return true;
+        }
+
+        private void AddTransactionLoop()
+        {
+            while (disposed == 0)
+            {
+                new_tx_event.WaitOne();
+                Transaction[] transactions;
+                lock (temp_pool)
+                {
+                    transactions = temp_pool.ToArray();
+                    temp_pool.Clear();
+                }
+                lock (mem_pool)
+                {
+                    transactions = transactions.Where(p => !mem_pool.ContainsKey(p.Hash) && !Blockchain.Default.ContainsTransaction(p.Hash)).ToArray();
+                    ConcurrentBag<Transaction> verified = new ConcurrentBag<Transaction>();
+                    transactions.AsParallel().ForAll(tx =>
+                    {
+                        if (tx.Verify(mem_pool.Values.Concat(transactions)))
+                            verified.Add(tx);
+                    });
+                    foreach (Transaction tx in verified)
+                        mem_pool.Add(tx.Hash, tx);
+                }
+            }
+        }
+
+        public static void AllowHashes(IEnumerable<UInt256> hashes)
+        {
+            lock (KnownHashes)
+            {
+                KnownHashes.ExceptWith(hashes);
+            }
+        }
+
+        private static void Blockchain_PersistCompleted(object sender, Block block)
+        {
+            lock (mem_pool)
+            {
+                foreach (Transaction tx in block.Transactions)
+                {
+                    mem_pool.Remove(tx.Hash);
+                }
+                if (mem_pool.Count == 0) return;
+                Transaction[] remain = mem_pool.Values.ToArray();
+                mem_pool.Clear();
+                foreach (Transaction tx in remain)
+                {
+                    AddTransaction(tx);
+                }
+            }
+        }
+
+        public async Task ConnectToPeerAsync(string hostNameOrAddress, int port)
+        {
+            IPAddress ipAddress;
+            if (IPAddress.TryParse(hostNameOrAddress, out ipAddress))
+            {
+                ipAddress = ipAddress.MapToIPv6();
+            }
+            else
+            {
+                IPHostEntry entry;
+                try
+                {
+                    entry = await Dns.GetHostEntryAsync(hostNameOrAddress);
+                }
+                catch (SocketException)
+                {
+                    return;
+                }
+                ipAddress = entry.AddressList.FirstOrDefault(p => p.AddressFamily == AddressFamily.InterNetwork || p.IsIPv6Teredo)?.MapToIPv6();
+                if (ipAddress == null) return;
+            }
+            await ConnectToPeerAsync(new IPEndPoint(ipAddress, port));
+        }
+
+        public async Task ConnectToPeerAsync(IPEndPoint remoteEndpoint)
+        {
+            if (remoteEndpoint.Port == Port && LocalAddresses.Contains(remoteEndpoint.Address)) return;
+            lock (unconnectedPeers)
+            {
+                unconnectedPeers.Remove(remoteEndpoint);
             }
             lock (connectedPeers)
             {
                 if (connectedPeers.Any(p => remoteEndpoint.Equals(p.ListenerEndpoint)))
                     return;
             }
-            TcpRemoteNode remoteNode = new TcpRemoteNode(this, remoteEndpoint);
+            TcpRemoteNode remoteNode = new TcpRemoteNode(this, remoteEndpoint);
             if (await remoteNode.ConnectAsync())
             {
                 OnConnected(remoteNode);
             }
-        }
-
-        private void ConnectToPeersLoop()
-        {
-            while (disposed == 0)
-            {
-                int connectedCount = connectedPeers.Count;
-                int unconnectedCount = unconnectedPeers.Count;
-                if (connectedCount < CONNECTED_MAX)
-                {
-                    Task[] tasks = { };
-                    if (unconnectedCount > 0)
-                    {
-                        IPEndPoint[] endpoints;
-                        lock (unconnectedPeers)
-                        {
-                            endpoints = unconnectedPeers.Take(CONNECTED_MAX - connectedCount).ToArray();
-                        }
-                        tasks = endpoints.Select(p => ConnectToPeerAsync(p)).ToArray();
-                    }
-                    else if (connectedCount > 0)
-                    {
-                        lock (connectedPeers)
-                        {
-                            foreach (RemoteNode node in connectedPeers)
-                                node.RequestPeers();
-                        }
-                    }
-                    else
-                    {
-                        tasks = Settings.Default.SeedList.OfType<string>().Select(p => p.Split(':')).Select(p => ConnectToPeerAsync(p[0], int.Parse(p[1]))).ToArray();
-                    }
-                    Task.WaitAll(tasks);
-                }
-                for (int i = 0; i < 50 && disposed == 0; i++)
-                {
-                    Thread.Sleep(100);
-                }
-            }
-        }
-
-        public static bool ContainsTransaction(UInt256 hash)
-        {
-            lock (MemoryPool)
-            {
-                return MemoryPool.ContainsKey(hash);
-            }
-        }
-
-        public void Dispose()
-        {
-            if (Interlocked.Exchange(ref disposed, 1) == 0)
-            {
-                if (started > 0)
-                {
-                    if (listener != null) listener.Stop();
-                    if (!connectThread.ThreadState.HasFlag(ThreadState.Unstarted)) connectThread.Join();
-                    lock (unconnectedPeers)
-                    {
-                        if (unconnectedPeers.Count < UNCONNECTED_MAX)
-                        {
-                            lock (connectedPeers)
-                            {
-                                unconnectedPeers.UnionWith(connectedPeers.Select(p => p.ListenerEndpoint).Where(p => p != null).Take(UNCONNECTED_MAX - unconnectedPeers.Count));
-                            }
-                        }
-                    }
-                    RemoteNode[] nodes;
-                    lock (connectedPeers)
-                    {
-                        nodes = connectedPeers.ToArray();
-                    }
-                    Task.WaitAll(nodes.Select(p => Task.Run(() => p.Disconnect(false))).ToArray());
-                }
-            }
-        }
-
-        public static IEnumerable<Transaction> GetMemoryPool()
-        {
-            lock (MemoryPool)
-            {
-                foreach (Transaction tx in MemoryPool.Values)
-                    yield return tx;
-            }
-        }
-
-        public RemoteNode[] GetRemoteNodes()
-        {
-            lock (connectedPeers)
-            {
-                return connectedPeers.ToArray();
-            }
-        }
-
-        public static Transaction GetTransaction(UInt256 hash)
-        {
-            lock (MemoryPool)
-            {
-                Transaction tx;
-                if (!MemoryPool.TryGetValue(hash, out tx))
-                    return null;
-                return tx;
-            }
-        }
-
-        private static bool IsIntranetAddress(IPAddress address)
-        {
-            byte[] data = address.MapToIPv4().GetAddressBytes();
-            Array.Reverse(data);
-            uint value = BitConverter.ToUInt32(data, 0);
-            return (value & 0xff000000) == 0x0a000000 || (value & 0xfff00000) == 0xac100000 || (value & 0xffff0000) == 0xc0a80000;
-        }
-
-        public static void LoadState(Stream stream)
-        {
-            unconnectedPeers.Clear();
-            using (BinaryReader reader = new BinaryReader(stream, Encoding.ASCII, true))
-            {
-                int count = reader.ReadInt32();
-                for (int i = 0; i < count; i++)
-                {
-                    IPAddress address = new IPAddress(reader.ReadBytes(4));
-                    int port = reader.ReadUInt16();
-                    unconnectedPeers.Add(new IPEndPoint(address.MapToIPv6(), port));
-                }
-            }
-        }
-
+        }
+
+        private void ConnectToPeersLoop()
+        {
+            while (disposed == 0)
+            {
+                int connectedCount = connectedPeers.Count;
+                int unconnectedCount = unconnectedPeers.Count;
+                if (connectedCount < CONNECTED_MAX)
+                {
+                    Task[] tasks = { };
+                    if (unconnectedCount > 0)
+                    {
+                        IPEndPoint[] endpoints;
+                        lock (unconnectedPeers)
+                        {
+                            endpoints = unconnectedPeers.Take(CONNECTED_MAX - connectedCount).ToArray();
+                        }
+                        tasks = endpoints.Select(p => ConnectToPeerAsync(p)).ToArray();
+                    }
+                    else if (connectedCount > 0)
+                    {
+                        lock (connectedPeers)
+                        {
+                            foreach (RemoteNode node in connectedPeers)
+                                node.RequestPeers();
+                        }
+                    }
+                    else
+                    {
+                        tasks = Settings.Default.SeedList.OfType<string>().Select(p => p.Split(':')).Select(p => ConnectToPeerAsync(p[0], int.Parse(p[1]))).ToArray();
+                    }
+                    Task.WaitAll(tasks);
+                }
+                for (int i = 0; i < 50 && disposed == 0; i++)
+                {
+                    Thread.Sleep(100);
+                }
+            }
+        }
+
+        public static bool ContainsTransaction(UInt256 hash)
+        {
+            lock (mem_pool)
+            {
+                return mem_pool.ContainsKey(hash);
+            }
+        }
+
+        public void Dispose()
+        {
+            if (Interlocked.Exchange(ref disposed, 1) == 0)
+            {
+                if (started > 0)
+                {
+                    if (listener != null) listener.Stop();
+                    if (!connectThread.ThreadState.HasFlag(ThreadState.Unstarted)) connectThread.Join();
+                    lock (unconnectedPeers)
+                    {
+                        if (unconnectedPeers.Count < UNCONNECTED_MAX)
+                        {
+                            lock (connectedPeers)
+                            {
+                                unconnectedPeers.UnionWith(connectedPeers.Select(p => p.ListenerEndpoint).Where(p => p != null).Take(UNCONNECTED_MAX - unconnectedPeers.Count));
+                            }
+                        }
+                    }
+                    RemoteNode[] nodes;
+                    lock (connectedPeers)
+                    {
+                        nodes = connectedPeers.ToArray();
+                    }
+                    Task.WaitAll(nodes.Select(p => Task.Run(() => p.Disconnect(false))).ToArray());
+                    new_tx_event.Set();
+                    if (poolThread?.ThreadState.HasFlag(ThreadState.Unstarted) == false)
+                        poolThread.Join();
+                    new_tx_event.Dispose();
+                }
+            }
+        }
+
+        public static IEnumerable<Transaction> GetMemoryPool()
+        {
+            lock (mem_pool)
+            {
+                foreach (Transaction tx in mem_pool.Values)
+                    yield return tx;
+            }
+        }
+
+        public RemoteNode[] GetRemoteNodes()
+        {
+            lock (connectedPeers)
+            {
+                return connectedPeers.ToArray();
+            }
+        }
+
+        public static Transaction GetTransaction(UInt256 hash)
+        {
+            lock (mem_pool)
+            {
+                Transaction tx;
+                if (!mem_pool.TryGetValue(hash, out tx))
+                    return null;
+                return tx;
+            }
+        }
+
+        private static bool IsIntranetAddress(IPAddress address)
+        {
+            byte[] data = address.MapToIPv4().GetAddressBytes();
+            Array.Reverse(data);
+            uint value = data.ToUInt32(0);
+            return (value & 0xff000000) == 0x0a000000 || (value & 0xfff00000) == 0xac100000 || (value & 0xffff0000) == 0xc0a80000;
+        }
+
+        public static void LoadState(Stream stream)
+        {
+            unconnectedPeers.Clear();
+            using (BinaryReader reader = new BinaryReader(stream, Encoding.ASCII, true))
+            {
+                int count = reader.ReadInt32();
+                for (int i = 0; i < count; i++)
+                {
+                    IPAddress address = new IPAddress(reader.ReadBytes(4));
+                    int port = reader.ReadUInt16();
+                    unconnectedPeers.Add(new IPEndPoint(address.MapToIPv6(), port));
+                }
+            }
+        }
+
         private void OnConnected(RemoteNode remoteNode)
         {
             lock (connectedPeers)
@@ -309,54 +345,61 @@ private void OnConnected(RemoteNode remoteNode)
             remoteNode.InventoryReceived += RemoteNode_InventoryReceived;
             remoteNode.PeersReceived += RemoteNode_PeersReceived;
             remoteNode.StartProtocol();
-        }
-
-        public bool Relay(IInventory inventory)
-        {
-            lock (KnownHashes)
-            {
-                if (!KnownHashes.Add(inventory.Hash)) return false;
-            }
-            if (inventory is Block)
-            {
-                if (Blockchain.Default == null) return false;
-                Block block = (Block)inventory;
-                if (Blockchain.Default.ContainsBlock(block.Hash)) return false;
-                if (!Blockchain.Default.AddBlock(block)) return false;
-            }
-            else if (inventory is Transaction)
-            {
-                if (!AddTransaction((Transaction)inventory)) return false;
-            }
-            else //if (inventory is Consensus)
-            {
-                if (!inventory.Verify()) return false;
-            }
-            bool relayed = false;
-            lock (connectedPeers)
-            {
-                RelayCache.Add(inventory);
-                foreach (RemoteNode node in connectedPeers)
-                    relayed |= node.Relay(inventory);
-            }
-            NewInventory?.Invoke(this, inventory);
-            return relayed;
-        }
-
-        private void RemoteNode_Disconnected(object sender, bool error)
-        {
-            RemoteNode remoteNode = (RemoteNode)sender;
-            remoteNode.Disconnected -= RemoteNode_Disconnected;
-            remoteNode.InventoryReceived -= RemoteNode_InventoryReceived;
-            remoteNode.PeersReceived -= RemoteNode_PeersReceived;
-            if (error && remoteNode.ListenerEndpoint != null)
-            {
-                lock (badPeers)
-                {
-                    badPeers.Add(remoteNode.ListenerEndpoint);
-                }
-            }
-            lock (unconnectedPeers)
+        }
+
+        public bool Relay(IInventory inventory)
+        {
+            if (inventory is MinerTransaction) return false;
+            lock (KnownHashes)
+            {
+                if (!KnownHashes.Add(inventory.Hash)) return false;
+            }
+            if (inventory is Block)
+            {
+                if (Blockchain.Default == null) return false;
+                Block block = (Block)inventory;
+                if (Blockchain.Default.ContainsBlock(block.Hash)) return false;
+                if (!Blockchain.Default.AddBlock(block)) return false;
+            }
+            else if (inventory is Transaction)
+            {
+                if (!AddTransaction((Transaction)inventory)) return false;
+            }
+            else //if (inventory is Consensus)
+            {
+                if (!inventory.Verify()) return false;
+            }
+            bool relayed = RelayDirectly(inventory);
+            NewInventory?.Invoke(this, inventory);
+            return relayed;
+        }
+
+        public bool RelayDirectly(IInventory inventory)
+        {
+            bool relayed = false;
+            lock (connectedPeers)
+            {
+                RelayCache.Add(inventory);
+                foreach (RemoteNode node in connectedPeers)
+                    relayed |= node.Relay(inventory);
+            }
+            return relayed;
+        }
+
+        private void RemoteNode_Disconnected(object sender, bool error)
+        {
+            RemoteNode remoteNode = (RemoteNode)sender;
+            remoteNode.Disconnected -= RemoteNode_Disconnected;
+            remoteNode.InventoryReceived -= RemoteNode_InventoryReceived;
+            remoteNode.PeersReceived -= RemoteNode_PeersReceived;
+            if (error && remoteNode.ListenerEndpoint != null)
+            {
+                lock (badPeers)
+                {
+                    badPeers.Add(remoteNode.ListenerEndpoint);
+                }
+            }
+            lock (unconnectedPeers)
             {
                 lock (connectedPeers)
                 {
@@ -365,86 +408,106 @@ private void RemoteNode_Disconnected(object sender, bool error)
                         unconnectedPeers.Remove(remoteNode.ListenerEndpoint);
                     }
                     connectedPeers.Remove(remoteNode);
-                }
-            }
-        }
-
-        private void RemoteNode_InventoryReceived(object sender, IInventory inventory)
-        {
-            Relay(inventory);
-        }
-
-        private void RemoteNode_PeersReceived(object sender, IPEndPoint[] peers)
-        {
-            lock (unconnectedPeers)
-            {
-                if (unconnectedPeers.Count < UNCONNECTED_MAX)
-                {
-                    lock (badPeers)
+                }
+            }
+        }
+
+        private void RemoteNode_InventoryReceived(object sender, IInventory inventory)
+        {
+            if (inventory is Transaction)
+            {
+                if (Blockchain.Default == null) return;
+                lock (KnownHashes)
+                {
+                    if (!KnownHashes.Add(inventory.Hash)) return;
+                }
+                lock (temp_pool)
+                {
+                    temp_pool.Add((Transaction)inventory);
+                }
+                new_tx_event.Set();
+            }
+            else
+            {
+                Relay(inventory);
+            }
+        }
+
+        private void RemoteNode_PeersReceived(object sender, IPEndPoint[] peers)
+        {
+            lock (unconnectedPeers)
+            {
+                if (unconnectedPeers.Count < UNCONNECTED_MAX)
+                {
+                    lock (badPeers)
                     {
                         lock (connectedPeers)
                         {
                             unconnectedPeers.UnionWith(peers);
                             unconnectedPeers.ExceptWith(badPeers);
                             unconnectedPeers.ExceptWith(connectedPeers.Select(p => p.ListenerEndpoint));
-                        }
-                    }
-                }
-            }
-        }
-
-        public static void SaveState(Stream stream)
-        {
-            IPEndPoint[] peers;
-            lock (unconnectedPeers)
-            {
-                peers = unconnectedPeers.Take(UNCONNECTED_MAX).ToArray();
-            }
-            using (BinaryWriter writer = new BinaryWriter(stream, Encoding.ASCII, true))
-            {
-                writer.Write(peers.Length);
-                foreach (IPEndPoint endpoint in peers)
-                {
-                    writer.Write(endpoint.Address.MapToIPv4().GetAddressBytes());
-                    writer.Write((ushort)endpoint.Port);
-                }
-            }
-        }
-
-        public async void Start(int port)
-        {
-            if (Interlocked.Exchange(ref started, 1) == 0)
-            {
-                IPAddress address = LocalAddresses.FirstOrDefault(p => p.IsIPv4MappedToIPv6 && !IsIntranetAddress(p));
-                if (address == null && UpnpEnabled && await UPnP.DiscoverAsync())
-                {
-                    try
-                    {
-                        address = await UPnP.GetExternalIPAsync();
-                        await UPnP.ForwardPortAsync(port, ProtocolType.Tcp, "AntShares");
-                        LocalAddresses.Add(address);
-                    }
-                    catch { }
-                }
-                listener = new TcpListener(IPAddress.Any, port);
-                try
-                {
-                    listener.Start();
-                    Port = (ushort)port;
-                }
-                catch (SocketException) { }
-                connectThread.Start();
-                if (Port > 0) await AcceptPeersAsync();
-            }
-        }
-
-        public void SynchronizeMemoryPool()
-        {
-            lock (connectedPeers)
-            {
-                foreach (RemoteNode node in connectedPeers)
-                    node.RequestMemoryPool();
-            }
-        }
-    }
-}
+                        }
+                    }
+                }
+            }
+        }
+
+        public static void SaveState(Stream stream)
+        {
+            IPEndPoint[] peers;
+            lock (unconnectedPeers)
+            {
+                peers = unconnectedPeers.Take(UNCONNECTED_MAX).ToArray();
+            }
+            using (BinaryWriter writer = new BinaryWriter(stream, Encoding.ASCII, true))
+            {
+                writer.Write(peers.Length);
+                foreach (IPEndPoint endpoint in peers)
+                {
+                    writer.Write(endpoint.Address.MapToIPv4().GetAddressBytes());
+                    writer.Write((ushort)endpoint.Port);
+                }
+            }
+        }
+
+        public void Start(int port)
+        {
+            if (Interlocked.Exchange(ref started, 1) == 0)
+            {
+                Task.Run(async () =>
+                {
+                    IPAddress address = LocalAddresses.FirstOrDefault(p => p.IsIPv4MappedToIPv6 && !IsIntranetAddress(p));
+                    if (address == null && UpnpEnabled && await UPnP.DiscoverAsync())
+                    {
+                        try
+                        {
+                            address = await UPnP.GetExternalIPAsync();
+                            await UPnP.ForwardPortAsync(port, ProtocolType.Tcp, "AntShares");
+                            LocalAddresses.Add(address);
+                        }
+                        catch { }
+                    }
+                    listener = new TcpListener(IPAddress.Any, port);
+                    try
+                    {
+                        listener.Start();
+                        Port = (ushort)port;
+                    }
+                    catch (SocketException) { }
+                    connectThread.Start();
+                    poolThread?.Start();
+                    if (Port > 0) await AcceptPeersAsync();
+                });
+            }
+        }
+
+        public void SynchronizeMemoryPool()
+        {
+            lock (connectedPeers)
+            {
+                foreach (RemoteNode node in connectedPeers)
+                    node.RequestMemoryPool();
+            }
+        }
+    }
+}
```
