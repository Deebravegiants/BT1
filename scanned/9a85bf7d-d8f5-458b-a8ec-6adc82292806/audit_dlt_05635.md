# [?] anacrolix/torrent: Serve peerconn panic fix (#20748)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-04-23
Source: https://github.com/erigontech/erigon/commit/2b1856faffd43ff1ab283d2200f6249eea6d5dd7
Type: security-commit

## Details
anacrolix/torrent: Serve peerconn panic fix (#20748)

Addresses https://github.com/erigontech/erigon-qa/issues/403 in main.
Needs to also be backported to 3.4.

Looks like a rare path where if there's an issue reading torrent data in
order to serve a peer request, then an invariant was broken and
triggered a logic panic. The fix ensures that on a bad read the
invariants are maintained.

Make sure to trigger the first 2 workflows per the issue to verify.

## Patch
### go.mod
```diff
@@ -18,15 +18,15 @@ require (
 	github.com/99designs/gqlgen v0.17.89
 	github.com/FastFilter/xorfilter v0.5.1
 	github.com/Masterminds/sprig/v3 v3.2.3
-	github.com/RoaringBitmap/roaring/v2 v2.14.4
+	github.com/RoaringBitmap/roaring/v2 v2.16.0
 	github.com/alecthomas/kong v1.15.0
 	github.com/anacrolix/envpprof v1.5.0
 	github.com/anacrolix/generics v0.2.0
 	github.com/anacrolix/go-libutp v1.3.3-0.20251121015447-f294e5ed5b4d
 	github.com/anacrolix/log v0.17.1-0.20251118025802-918f1157b7bb
 	github.com/anacrolix/missinggo/v2 v2.10.0
 	github.com/anacrolix/sync v0.5.5-0.20251119100342-d78dd1f686f1
-	github.com/anacrolix/torrent v1.61.1-0.20260306043331-7dea980541ac
+	github.com/anacrolix/torrent v1.61.1-0.20260423052610-0aa61207b935
 	github.com/benesch/cgosymbolizer v0.0.0-20190515212042-bec6fe6e597b
 	github.com/c2h5oh/datasize v0.0.0-20231215233829-aa82cc1e6500
 	github.com/cenkalti/backoff/v4 v4.3.0
@@ -150,7 +150,6 @@ require (
 	github.com/Masterminds/semver/v3 v3.4.0 // indirect
 	github.com/MirrexOne/unqueryvet v1.5.4 // indirect
 	github.com/OpenPeeDeeP/depguard/v2 v2.2.1 // indirect
-	github.com/RoaringBitmap/roaring v1.9.4 // indirect
 	github.com/agnivade/levenshtein v1.2.1 // indirect
 	github.com/alecthomas/atomic v0.1.0-alpha2 // indirect
 	github.com/alecthomas/chroma/v2 v2.23.1 // indirect
```

### go.sum
```diff
@@ -73,10 +73,8 @@ github.com/PuerkitoBio/goquery v1.11.0/go.mod h1:wQHgxUOU3JGuj3oD/QFfxUdlzW6xPHf
 github.com/RoaringBitmap/roaring v0.4.7/go.mod h1:8khRDP4HmeXns4xIj9oGrKSz7XTQiJx2zgh7AcNke4w=
 github.com/RoaringBitmap/roaring v0.4.17/go.mod h1:D3qVegWTmfCaX4Bl5CrBE9hfrSrrXIr8KVNvRsDi1NI=
 github.com/RoaringBitmap/roaring v0.4.23/go.mod h1:D0gp8kJQgE1A4LQ5wFLggQEyvDi06Mq5mKs52e1TwOo=
-github.com/RoaringBitmap/roaring v1.9.4 h1:yhEIoH4YezLYT04s1nHehNO64EKFTop/wBhxv2QzDdQ=
-github.com/RoaringBitmap/roaring v1.9.4/go.mod h1:6AXUsoIEzDTFFQCe1RbGA6uFONMhvejWj5rqITANK90=
-github.com/RoaringBitmap/roaring/v2 v2.14.4 h1:4aKySrrg9G/5oRtJ3TrZLObVqxgQ9f1znCRBwEwjuVw=
-github.com/RoaringBitmap/roaring/v2 v2.14.4/go.mod h1:oMvV6omPWr+2ifRdeZvVJyaz+aoEUopyv5iH0u/+wbY=
+github.com/RoaringBitmap/roaring/v2 v2.16.0 h1:Kys1UNf49d5W8Tq3bpuAhIr/Z8/yPB+59CO8A6c/BbE=
+github.com/RoaringBitmap/roaring/v2 v2.16.0/go.mod h1:eq4wdNXxtJIS/oikeCzdX1rBzek7ANzbth041hrU8Q4=
 github.com/Shopify/sarama v1.19.0/go.mod h1:FVkBWblsNy7DGZRfXLU0O9RCGt5g3g3yEuWXgklEdEo=
 github.com/Shopify/toxiproxy v2.1.4+incompatible/go.mod h1:OXgGpZ6Cli1/URJOF1DMxUHB2q5Ap20/P/eIdh4G0pI=
 github.com/agnivade/levenshtein v1.2.1 h1:EHBY3UOn1gwdy/VbFwgo4cxecRznFk7fKWN1KOX7eoM=
@@ -155,8 +153,8 @@ github.com/anacrolix/sync v0.5.5-0.20251119100342-d78dd1f686f1/go.mod h1:21cUWer
 github.com/anacrolix/tagflag v0.0.0-20180109131632-2146c8d41bf0/go.mod h1:1m2U/K6ZT+JZG0+bdMK6qauP49QT4wE5pmhJXOKKCHw=
 github.com/anacrolix/tagflag v1.0.0/go.mod h1:1m2U/K6ZT+JZG0+bdMK6qauP49QT4wE5pmhJXOKKCHw=
 github.com/anacrolix/tagflag v1.1.0/go.mod h1:Scxs9CV10NQatSmbyjqmqmeQNwGzlNe0CMUMIxqHIG8=
-github.com/anacrolix/torrent v1.61.1-0.20260306043331-7dea980541ac h1:gpzbmV0sooJvesid+HTgoG/bR8IS38k6jbD1hyHI04M=
-github.com/anacrolix/torrent v1.61.1-0.20260306043331-7dea980541ac/go.mod h1:CJaFHVYZv9k3btNExGGHIXjI6vvGb10QoCRWOKpUd10=
+github.com/anacrolix/torrent v1.61.1-0.20260423052610-0aa61207b935 h1:7zYUWXNTCDMQSTO/SIYUOXbn/tEp5D5wWQJycahpst0=
+github.com/anacrolix/torrent v1.61.1-0.20260423052610-0aa61207b935/go.mod h1:WOyzkjUtFTK7sZNqgGtoAmWLUsJ0XIwyvw0zLI63h7M=
 github.com/anacrolix/upnp v0.1.4 h1:+2t2KA6QOhm/49zeNyeVwDu1ZYS9dB9wfxyVvh/wk7U=
 github.com/anacrolix/upnp v0.1.4/go.mod h1:Qyhbqo69gwNWvEk1xNTXsS5j7hMHef9hdr984+9fIic=
 github.com/anacrolix/utp v0.1.0 h1:FOpQOmIwYsnENnz7tAGohA+r6iXpRjrq8ssKSre2Cp4=
@@ -194,7 +192,6 @@ github.com/beorn7/perks v0.0.0-20180321164747-3a771d992973/go.mod h1:Dwedo/Wpr24
 github.com/beorn7/perks v1.0.0/go.mod h1:KWe93zE9D1o94FZ5RNwFwVgaQK1VOXiVxmqh+CedLV8=
 github.com/beorn7/perks v1.0.1 h1:VlbKKnNfV8bJzeqoa4cOKqO6bYr3WgKZxO8Z16+hsOM=
 github.com/beorn7/perks v1.0.1/go.mod h1:G2ZrVWU2WbWT9wwq4/hrbKbnv/1ERSJQ0ibhJ6rlkpw=
-github.com/bits-and-blooms/bitset v1.12.0/go.mod h1:7hO7Gc7Pp1vODcmWvKMRA9BNmbv6a/7QIWpPxHddWR8=
 github.com/bits-and-blooms/bitset v1.24.4 h1:95H15Og1clikBrKr/DuzMXkQzECs1M6hhoGXLwLQOZE=
 github.com/bits-and-blooms/bitset v1.24.4/go.mod h1:7hO7Gc7Pp1vODcmWvKMRA9BNmbv6a/7QIWpPxHddWR8=
 github.com/bkielbasa/cyclop v1.2.3 h1:faIVMIGDIANuGPWH031CZJTi2ymOQBULs9H21HSMa5w=
```
