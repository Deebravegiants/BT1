# [?] fix(cometbft) Prevent panic on non-nil proposal without vote extensions (#3270)

## Summary
Severity: Unknown
Chain: Cosmos Hub
Component: cosmos/gaia
Published: 2024-08-19
Source: https://github.com/cosmos/gaia/commit/c5ff8d200502f84f318c04fd69a39577f6539833
Type: security-commit

## Details
fix(cometbft) Prevent panic on non-nil proposal without vote extensions (#3270)

* fix(cometbft) Prevent panic on non-nil proposal without vote extensions

* Update changelog files for PR 3270 feedback

Co-authored-by: Marius Poke <marius.poke@posteo.de>

---------

Co-authored-by: Marius Poke <marius.poke@posteo.de>

## Patch
### .changelog/unreleased/dependencies/3270-bump-cometbft.md
```diff
@@ -0,0 +1,3 @@
+- Bump [cometbft](https://github.com/cometbft/cometbft) to
+   [v0.38.11](https://github.com/cometbft/cometbft/releases/tag/v0.38.11)
+   ([\#3270](https://github.com/cosmos/gaia/pull/3270)
```

### go.mod
```diff
@@ -18,7 +18,7 @@ require (
 	cosmossdk.io/x/tx v0.13.4
 	cosmossdk.io/x/upgrade v0.1.4
 	github.com/CosmWasm/wasmd v0.51.0
-	github.com/cometbft/cometbft v0.38.9
+	github.com/cometbft/cometbft v0.38.11
 	github.com/cometbft/cometbft-db v0.12.0
 	github.com/cosmos/cosmos-db v1.0.2
 	github.com/cosmos/cosmos-sdk v0.50.8
@@ -163,7 +163,6 @@ require (
 	github.com/kr/pretty v0.3.1 // indirect
 	github.com/kr/text v0.2.0 // indirect
 	github.com/lib/pq v1.10.9 // indirect
-	github.com/libp2p/go-buffer-pool v0.1.0 // indirect
 	github.com/linxGnu/grocksdb v1.8.14 // indirect
 	github.com/magiconair/properties v1.8.7 // indirect
 	github.com/manifoldco/promptui v0.9.0 // indirect
```

### go.sum
```diff
@@ -398,8 +398,8 @@ github.com/codahale/hdrhistogram v0.0.0-20161010025455-3a0bb77429bd/go.mod h1:sE
 github.com/coinbase/kryptology v1.8.0/go.mod h1:RYXOAPdzOGUe3qlSFkMGn58i3xUA8hmxYHksuq+8ciI=
 github.com/coinbase/rosetta-sdk-go v0.7.9 h1:lqllBjMnazTjIqYrOGv8h8jxjg9+hJazIGZr9ZvoCcA=
 github.com/coinbase/rosetta-sdk-go v0.7.9/go.mod h1:0/knutI7XGVqXmmH4OQD8OckFrbQ8yMsUZTG7FXCR2M=
-github.com/cometbft/cometbft v0.38.9 h1:cJBJBG0mPKz+sqelCi/hlfZjadZQGdDNnu6YQ1ZsUHQ=
-github.com/cometbft/cometbft v0.38.9/go.mod h1:xOoGZrtUT+A5izWfHSJgl0gYZUE7lu7Z2XIS1vWG/QQ=
+github.com/cometbft/cometbft v0.38.11 h1:6bNDUB8/xq4uYonYwIfGc9OqK1ZH4NkdaMmR1LZIJqk=
+github.com/cometbft/cometbft v0.38.11/go.mod h1:jHPx9vQpWzPHEAiYI/7EDKaB1NXhK6o3SArrrY8ExKc=
 github.com/cometbft/cometbft-db v0.12.0 h1:v77/z0VyfSU7k682IzZeZPFZrQAKiQwkqGN0QzAjMi0=
 github.com/cometbft/cometbft-db v0.12.0/go.mod h1:aX2NbCrjNVd2ZajYxt1BsiFf/Z+TQ2MN0VxdicheYuw=
 github.com/consensys/bavard v0.1.8-0.20210406032232-f3452dc9b572/go.mod h1:Bpd0/3mZuaj6Sj+PqrmIquiOKy397AKGThQPaGzNXAQ=
@@ -944,8 +944,6 @@ github.com/leodido/go-urn v1.2.1/go.mod h1:zt4jvISO2HfUBqxjfIshjdMTYS56ZS/qv49ic
 github.com/lib/pq v1.0.0/go.mod h1:5WUZQaWbwv1U+lTReE5YruASi9Al49XbQIvNi/34Woo=
 github.com/lib/pq v1.10.9 h1:YXG7RB+JIjhP29X+OtkiDnYaXQwpS4JEWq7dtCCRUEw=
 github.com/lib/pq v1.10.9/go.mod h1:AlVN5x4E4T544tWzH6hKfbfQvm3HdbOxrmggDNAPY9o=
-github.com/libp2p/go-buffer-pool v0.1.0 h1:oK4mSFcQz7cTQIfqbe4MIj9gLW+mnanjyFtc6cdF0Y8=
-github.com/libp2p/go-buffer-pool v0.1.0/go.mod h1:N+vh8gMqimBzdKkSMVuydVDq+UV5QTWy5HSiZacSbPg=
 github.com/lightstep/lightstep-tracer-common/golang/gogo v0.0.0-20190605223551-bc2310a04743/go.mod h1:qklhhLq1aX+mtWk9cPHPzaBjWImj5ULL6C7HFJtXQMM=
 github.com/lightstep/lightstep-tracer-go v0.18.1/go.mod h1:jlF1pusYV4pidLvZ+XD0UBX0ZE6WURAspgAczcDHrL4=
 github.com/linxGnu/grocksdb v1.8.14 h1:HTgyYalNwBSG/1qCQUIott44wU5b2Y9Kr3z7SK5OfGQ=
```
