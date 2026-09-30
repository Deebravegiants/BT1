# [?] fix: patch comet bft (GHSA-hrhf-2vcr-ghch) (#1209)

## Summary
Severity: Unknown
Chain: Cronos
Component: crypto-org-chain/chain-main
Published: 2025-10-15
Source: https://github.com/crypto-org-chain/chain-main/commit/c2a0f6e5061eb0f884fe7231a3456c95526385dc
Type: security-commit

## Details
fix: patch comet bft (GHSA-hrhf-2vcr-ghch) (#1209)

* patch cometbft

* changelog

## Patch
### CHANGELOG.md
```diff
@@ -2,6 +2,10 @@
 
 ## UNRELEASED
 
+### Bugfixes
+- [#1209](https://github.com/crypto-org-chain/chain-main/pull/1209) Patch comet bft (GHSA-hrhf-2vcr-ghch)
+
+
 *July 9, 2025*
 
 ## v7.0.0
```

### go.mod
```diff
@@ -17,7 +17,7 @@ require (
 	cosmossdk.io/x/feegrant v0.1.1
 	cosmossdk.io/x/tx v0.13.7
 	cosmossdk.io/x/upgrade v0.1.4
-	github.com/cometbft/cometbft v0.38.17
+	github.com/cometbft/cometbft v0.38.19
 	github.com/cosmos/cosmos-db v1.1.1
 	github.com/cosmos/cosmos-proto v1.0.0-beta.5
 	github.com/cosmos/cosmos-sdk v0.50.14
@@ -34,8 +34,8 @@ require (
 	github.com/imdario/mergo v0.3.13
 	github.com/linxGnu/grocksdb v1.9.2
 	github.com/spf13/cast v1.7.1
-	github.com/spf13/cobra v1.8.1
-	github.com/spf13/pflag v1.0.5
+	github.com/spf13/cobra v1.9.1
+	github.com/spf13/pflag v1.0.6
 	github.com/stretchr/testify v1.10.0
 	google.golang.org/genproto/googleapis/api v0.0.0-20250106144421-5f5ef82da422
 	google.golang.org/grpc v1.71.0
@@ -89,7 +89,7 @@ require (
 	github.com/crypto-org-chain/cronos/memiavl v0.0.5-0.20231225065237-42f2597fca49 // indirect
 	github.com/danieljoos/wincred v1.2.1 // indirect
 	github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc // indirect
-	github.com/decred/dcrd/dcrec/secp256k1/v4 v4.3.0 // indirect
+	github.com/decred/dcrd/dcrec/secp256k1/v4 v4.4.0 // indirect
 	github.com/desertbit/timer v1.0.1 // indirect
 	github.com/dgraph-io/badger/v4 v4.2.0 // indirect
 	github.com/dgraph-io/ristretto v0.1.1 // indirect
@@ -144,7 +144,7 @@ require (
 	github.com/inconshreveable/mousetrap v1.1.0 // indirect
 	github.com/jmespath/go-jmespath v0.4.0 // indirect
 	github.com/jmhodges/levigo v1.0.0 // indirect
-	github.com/klauspost/compress v1.17.9 // indirect
+	github.com/klauspost/compress v1.17.11 // indirect
 	github.com/kr/pretty v0.3.1 // indirect
 	github.com/kr/text v0.2.0 // indirect
 	github.com/ledgerwatch/erigon-lib v0.0.0-20230210071639-db0e7ed11263 // indirect
@@ -165,7 +165,7 @@ require (
 	github.com/petermattis/goid v0.0.0-20240813172612-4fcff4a6cae7 // indirect
 	github.com/pkg/errors v0.9.1 // indirect
 	github.com/pmezard/go-difflib v1.0.1-0.20181226105442-5d4384ee4fb2 // indirect
-	github.com/prometheus/client_golang v1.20.5 // indirect
+	github.com/prometheus/client_golang v1.21.0 // indirect
 	github.com/prometheus/client_model v0.6.1 // indirect
 	github.com/prometheus/common v0.62.0 // indirect
 	github.com/prometheus/procfs v0.15.1 // indirect
```

### go.sum
```diff
@@ -835,8 +835,8 @@ github.com/codahale/hdrhistogram v0.0.0-20161010025455-3a0bb77429bd/go.mod h1:sE
 github.com/coinbase/kryptology v1.8.0/go.mod h1:RYXOAPdzOGUe3qlSFkMGn58i3xUA8hmxYHksuq+8ciI=
 github.com/coinbase/rosetta-sdk-go v0.7.9 h1:lqllBjMnazTjIqYrOGv8h8jxjg9+hJazIGZr9ZvoCcA=
 github.com/coinbase/rosetta-sdk-go v0.7.9/go.mod h1:0/knutI7XGVqXmmH4OQD8OckFrbQ8yMsUZTG7FXCR2M=
-github.com/cometbft/cometbft v0.38.17 h1:FkrQNbAjiFqXydeAO81FUzriL4Bz0abYxN/eOHrQGOk=
-github.com/cometbft/cometbft v0.38.17/go.mod h1:5l0SkgeLRXi6bBfQuevXjKqML1jjfJJlvI1Ulp02/o4=
+github.com/cometbft/cometbft v0.38.19 h1:vNdtCkvhuwUlrcLPAyigV7lQpmmo+tAq8CsB8gZjEYw=
+github.com/cometbft/cometbft v0.38.19/go.mod h1:UCu8dlHqvkAsmAFmWDRWNZJPlu6ya2fTWZlDrWsivwo=
 github.com/cometbft/cometbft-db v0.14.1 h1:SxoamPghqICBAIcGpleHbmoPqy+crij/++eZz3DlerQ=
 github.com/cometbft/cometbft-db v0.14.1/go.mod h1:KHP1YghilyGV/xjD5DP3+2hyigWx0WTp9X+0Gnx0RxQ=
 github.com/consensys/bavard v0.1.8-0.20210406032232-f3452dc9b572/go.mod h1:Bpd0/3mZuaj6Sj+PqrmIquiOKy397AKGThQPaGzNXAQ=
@@ -884,7 +884,7 @@ github.com/cosmos/rosetta-sdk-go v0.10.0 h1:E5RhTruuoA7KTIXUcMicL76cffyeoyvNybzU
 github.com/cosmos/rosetta-sdk-go v0.10.0/go.mod h1:SImAZkb96YbwvoRkzSMQB6noNJXFgWl/ENIznEoYQI4=
 github.com/cpuguy83/go-md2man v1.0.10/go.mod h1:SmD6nW6nTyfqj6ABTjUi3V3JVMnlJmwcJI5acqYI6dE=
 github.com/cpuguy83/go-md2man/v2 v2.0.0-20190314233015-f79a8a8ca69d/go.mod h1:maD7wRr/U5Z6m/iR4s+kqSMx2CaBsrgA7czyZG/E6dU=
-github.com/cpuguy83/go-md2man/v2 v2.0.4/go.mod h1:tgQtvFlXSQOSOSIRvRPT7W67SCa46tRHOmNcaadrF8o=
+github.com/cpuguy83/go-md2man/v2 v2.0.6/go.mod h1:oOW0eioCTA6cOiMLiUPZOpcVxMig6NIQQ7OS05n1F4g=
 github.com/creachadair/atomicfile v0.3.1 h1:yQORkHjSYySh/tv5th1dkKcn02NEW5JleB84sjt+W4Q=
 github.com/creachadair/atomicfile v0.3.1/go.mod h1:mwfrkRxFKwpNAflYZzytbSwxvbK6fdGRRlp0KEQc0qU=
 github.com/creachadair/tomledit v0.0.24 h1:5Xjr25R2esu1rKCbQEmjZYlrhFkDspoAbAKb6QKQDhQ=
@@ -908,11 +908,11 @@ github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc h1:U9qPSI2PIWSS1
 github.com/davecgh/go-spew v1.1.2-0.20180830191138-d8f796af33cc/go.mod h1:J7Y8YcW2NihsgmVo/mv3lAwl/skON4iLHjSsI+c5H38=
 github.com/deckarep/golang-set v1.8.0/go.mod h1:5nI87KwE7wgsBU1F4GKAw2Qod7p5kyS383rP6+o6qqo=
 github.com/decred/dcrd/crypto/blake256 v1.0.0/go.mod h1:sQl2p6Y26YV+ZOcSTP6thNdn47hh8kt6rqSlvmrXFAc=
-github.com/decred/dcrd/crypto/blake256 v1.0.1 h1:7PltbUIQB7u/FfZ39+DGa/ShuMyJ5ilcvdfma9wOH6Y=
-github.com/decred/dcrd/crypto/blake256 v1.0.1/go.mod h1:2OfgNZ5wDpcsFmHmCK5gZTPcCXqlm2ArzUIkw9czNJo=
+github.com/decred/dcrd/crypto/blake256 v1.1.0 h1:zPMNGQCm0g4QTY27fOCorQW7EryeQ/U0x++OzVrdms8=
+github.com/decred/dcrd/crypto/blake256 v1.1.0/go.mod h1:2OfgNZ5wDpcsFmHmCK5gZTPcCXqlm2ArzUIkw9czNJo=
 github.com/decred/dcrd/dcrec/secp256k1/v4 v4.0.1/go.mod h1:hyedUtir6IdtD/7lIxGeCxkaw7y45JueMRL4DIyJDKs=
-github.com/decred/dcrd/dcrec/secp256k1/v4 v4.3.0 h1:rpfIENRNNilwHwZeG5+P150SMrnNEcHYvcCuK6dPZSg=
-github.com/decred/dcrd/dcrec/secp256k1/v4 v4.3.0/go.mod h1:v57UDF4pDQJcEfFUCRop3lJL149eHGSe9Jvczhzjo/0=
+github.com/decred/dcrd/dcrec/secp256k1/v4 v4.4.0 h1:NMZiJj8QnKe1LgsbDayM4UoHwbvwDRwnI3hwNaAHRnc=
+github.com/decred/dcrd/dcrec/secp256k1/v4 v4.4.0/go.mod h1:ZXNYxsqcloTdSy/rNShjYzMhyjf0LaoftYK0p+A3h40=
 github.com/decred/dcrd/lru v1.0.0/go.mod h1:mxKOwFd7lFjN2GZYsiz/ecgqR6kkYAl+0pz0tEMk218=
 github.com/deepmap/oapi-codegen v1.6.0/go.mod h1:ryDa9AgbELGeB+YEXE1dR53yAjHwFvE9iAUlWl9Al3M=
 github.com/deepmap/oapi-codegen v1.8.2/go.mod h1:YLgSKSDv/bZQB7N4ws6luhozi3cEdRktEqrX88CvjIw=
@@ -1368,8 +1368,8 @@ github.com/klauspost/compress v1.11.7/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYs
 github.com/klauspost/compress v1.12.3/go.mod h1:8dP1Hq4DHOhN9w426knH3Rhby4rFm6D8eO+e+Dq5Gzg=
 github.com/klauspost/compress v1.15.9/go.mod h1:PhcZ0MbTNciWF3rruxRgKxI5NkcHHrHUDtV4Yw2GlzU=
 github.com/klauspost/compress v1.15.11/go.mod h1:QPwzmACJjUTFsnSHH934V6woptycfrDDJnH7hvFVbGM=
-github.com/klauspost/compress v1.17.9 h1:6KIumPrER1LHsvBVuDa0r5xaG0Es51mhhB9BQB2qeMA=
-github.com/klauspost/compress v1.17.9/go.mod h1:Di0epgTjJY877eYKx5yC51cX2A2Vl2ibi7bDH9ttBbw=
+github.com/klauspost/compress v1.17.11 h1:In6xLpyWOi1+C7tXUUWv2ot1QvBjxevKAaI6IXrJmUc=
+github.com/klauspost/compress v1.17.11/go.mod h1:pMDklpSncoRMuLFrf1W9Ss9KT+0rH90U12bZKk7uwG0=
 github.com/klauspost/cpuid v0.0.0-20170728055534-ae7887de9fa5/go.mod h1:Pj4uuM528wm8OyEC2QMXAi2YiTZ96dNQPGgoMS4s3ek=
 github.com/klauspost/cpuid/v2 v2.0.9/go.mod h1:FInQzS24/EEf25PyTYn52gqo7WaD8xa0213Md/qVLRg=
 github.com/klauspost/crc32 v0.0.0-20161016154125-cb6bfca970f6/go.mod h1:+ZoRqAPRLkC4NPOvfYeR5KNOrY6TD+/sAC3HXPZgDYg=
@@ -1575,8 +1575,8 @@ github.com/prometheus/client_golang v1.0.0/go.mod h1:db9x61etRT2tGnBNRi70OPL5Fsn
 github.com/prometheus/client_golang v1.3.0/go.mod h1:hJaj2vgQTGQmVCsAACORcieXFeDPbaTKGT+JTgUa3og=
 github.com/prometheus/client_golang v1.4.0/go.mod h1:e9GMxYsXl05ICDXkRhurwBS4Q3OK1iX/F2sw+iXX5zU=
 github.com/prometheus/client_golang v1.7.1/go.mod h1:PY5Wy2awLA44sXw4AOSfFBetzPP4j5+D6mVACh+pe2M=
-github.com/prometheus/client_golang v1.20.5 h1:cxppBPuYhUnsO6yo/aoRol4L7q7UFfdm+bR9r+8l63Y=
-github.com/prometheus/client_golang v1.20.5/go.mod h1:PIEt8X02hGcP8JWbeHyeZ53Y/jReSnHgO035n//V5WE=
+github.com/prometheus/client_golang v1.21.0 h1:DIsaGmiaBkSangBgMtWdNfxbMNdku5IK6iNhrEqWvdA=
+github.com/prometheus/client_golang v1.21.0/go.mod h1:U9NM32ykUErtVBxdvD3zfi+EuFkkaBvMb09mIfe0Zgg=
 github.com/prometheus/client_model v0.0.0-20180712105110-5c3871d89910/go.mod h1:MbSGuTsp3dbXC40dX6PRTWyKYBIrTGTE9sqQNg2J8bo=
 github.com/prometheus/client_model v0.0.0-20190115171406-56726106282f/go.mod h1:MbSGuTsp3dbXC40dX6PRTWyKYBIrTGTE9sqQNg2J8bo=
 github.com/prometheus/client_model v0.0.0-20190129233127-fd36f4220a90/go.mod h1:xMI15A0UPsDsEKsMN9yxemIoYk6Tm2C1GtYGdfGttqA=
@@ -1670,13 +1670,14 @@ github.com/spf13/cast v1.7.1 h1:cuNEagBQEHWN1FnbGEjCXL2szYEXqfJPbP2HNUaca9Y=
 github.com/spf13/cast v1.7.1/go.mod h1:ancEpBxwJDODSW/UG4rDrAqiKolqNNh2DX3mk86cAdo=
 github.com/spf13/cobra v0.0.3/go.mod h1:1l0Ry5zgKvJasoi3XT1TypsSe7PqH0Sj9dhYf7v3XqQ=
 github.com/spf13/cobra v0.0.5/go.mod h1:3K3wKZymM7VvHMDS9+Akkh4K60UwM26emMESw8tLCHU=
-github.com/spf13/cobra v1.8.1 h1:e5/vxKd/rZsfSJMUX1agtjeTDf+qv1/JdBF8gg5k9ZM=
-github.com/spf13/cobra v1.8.1/go.mod h1:wHxEcudfqmLYa8iTfL+OuZPbBZkmvliBWKIezN3kD9Y=
+github.com/spf13/cobra v1.9.1 h1:CXSaggrXdbHK9CF+8ywj8Amf7PBRmPCOJugH954Nnlo=
+github.com/spf13/cobra v1.9.1/go.mod h1:nDyEzZ8ogv936Cinf6g1RU9MRY64Ir93oCnqb9wxYW0=
 github.com/spf13/jwalterweatherman v1.0.0/go.mod h1:cQK4TGJAtQXfYWX+Ddv3mKDzgVb68N+wFjFa4jdeBTo=
 github.com/spf13/pflag v1.0.1/go.mod h1:DYY7MBk1bdzusC3SYhjObp+wFpr4gzcvqqNjLnInEg4=
 github.com/spf13/pflag v1.0.3/go.mod h1:DYY7MBk1bdzusC3SYhjObp+wFpr4gzcvqqNjLnInEg4=
-github.com/spf13/pflag v1.0.5 h1:iy+VFUOCP1a+8yFto/drg2CJ5u0yRoB7fZw3DKv/JXA=
 github.com/spf13/pflag v1.0.5/go.mod h1:McXfInJRrz4CZXVZOBLb0bTZqETkiAhM9Iw0y3An2Bg=
+github.com/spf13/pflag v1.0.6 h1:jFzHGLGAlb3ruxLB8MhbI6A8+AQX/2eW4qeyNZXNp2o=
+github.com/spf13/pflag v1.0.6/go.mod h1:McXfInJRrz4CZXVZOBLb0bTZqETkiAhM9Iw0y3An2Bg=
 github.com/spf13/viper v1.3.2/go.mod h1:ZiWeW+zYFKm7srdB9IoDzzZXaJaI5eL9QjNiN/DMA2s=
 github.com/spf13/viper v1.19.0 h1:RWq5SEjt8o25SROyN3z2OrDB9l7RPd3lwTWU8EcEdcI=
 github.com/spf13/viper v1.19.0/go.mod h1:GQUN9bilAbhU/jgc1bKs99f/suXKeUMct8Adx5+Ntkg=
```

### gomod2nix.toml
```diff
@@ -141,8 +141,8 @@ schema = 3
     version = "v0.7.9"
     hash = "sha256-ZWIXIXcHGjeCNgMrpXymry8/8esDDauGFfF/+gEoO1Y="
   [mod."github.com/cometbft/cometbft"]
-    version = "v0.38.17"
-    hash = "sha256-JjFTmg7v+4vk+r50BJ/dXi6Oz7Lcoxr6koW/DvmaQSI="
+    version = "v0.38.19"
+    hash = "sha256-mhWIhRVJ5dL3v7hfkhX9jiPfuvWN1FsegxBEWuKuBRc="
   [mod."github.com/cometbft/cometbft-db"]
     version = "v0.14.1"
     hash = "sha256-QvWMRGsdgCsSfL+DHp3w1Bm4jXa14SeT7oRK3PiNGV0="
@@ -214,8 +214,8 @@ schema = 3
     version = "v1.1.2-0.20180830191138-d8f796af33cc"
     hash = "sha256-fV9oI51xjHdOmEx6+dlq7Ku2Ag+m/bmbzPo6A4Y74qc="
   [mod."github.com/decred/dcrd/dcrec/secp256k1/v4"]
-    version = "v4.3.0"
-    hash = "sha256-ADbhI5Ad+q3OxooIiYeLAq5mMONk1gPIAnTch9zKsIM="
+    version = "v4.4.0"
+    hash = "sha256-qrhEIwhDll3cxoVpMbm1NQ9/HTI42S7ms8Buzlo5HCg="
   [mod."github.com/desertbit/timer"]
     version = "v1.0.1"
     hash = "sha256-Uk1Ep6lHLGEadcSF/2R9Bk6zwc5OUbTf/WCHrPatWEM="
@@ -397,8 +397,8 @@ schema = 3
     version = "v1.0.0"
     hash = "sha256-xEd0mDBeq3eR/GYeXjoTVb2sPs8sTCosn5ayWkcgENI="
   [mod."github.com/klauspost/compress"]
-    version = "v1.17.9"
-    hash = "sha256-FxHk4OuwsbiH1OLI+Q0oA4KpcOB786sEfik0G+GNoow="
+    version = "v1.17.11"
+    hash = "sha256-LFSIWy0C4VbiuPve0eKHr7Q7s4XtaGzsZ3qpO+6bEgc="
   [mod."github.com/kr/pretty"]
     version = "v0.3.1"
     hash = "sha256-DlER7XM+xiaLjvebcIPiB12oVNjyZHuJHoRGITzzpKU="
@@ -463,8 +463,8 @@ schema = 3
     version = "v1.0.1-0.20181226105442-5d4384ee4fb2"
     hash = "sha256-XA4Oj1gdmdV/F/+8kMI+DBxKPthZ768hbKsO3d9Gx90="
   [mod."github.com/prometheus/client_golang"]
-    version = "v1.20.5"
-    hash = "sha256-RbDZTBH+j2ZNLbHSMFxW0j8UStvkwc4IHTz3My9w4qo="
+    version = "v1.21.0"
+    hash = "sha256-ZK2NxVg1GSAa3ZYwpgc53KQcyjgdqYUpPCjvDxLkzc4="
   [mod."github.com/prometheus/client_model"]
     version = "v0.6.1"
     hash = "sha256-rIDyUzNfxRA934PIoySR0EhuBbZVRK/25Jlc/r8WODw="
@@ -505,11 +505,11 @@ schema = 3
     version = "v1.7.1"
     hash = "sha256-BjX0aY/PC37gIdMc7JhMgvhWFsksGdAcp2FgzpuvkPo="
   [mod."github.com/spf13/cobra"]
-    version = "v1.8.1"
-    hash = "sha256-yDF6yAHycV1IZOrt3/hofR+QINe+B2yqkcIaVov3Ky8="
+    version = "v1.9.1"
+    hash = "sha256-dzEqquABE3UqZmJuj99244QjvfojS8cFlsPr/MXQGj0="
   [mod."github.com/spf13/pflag"]
-    version = "v1.0.5"
-    hash = "sha256-w9LLYzxxP74WHT4ouBspH/iQZXjuAh2WQCHsuvyEjAw="
+    version = "v1.0.6"
+    hash = "sha256-NjrK0FZPIfO/p2xtL1J7fOBQNTZAPZOC6Cb4aMMvhxI="
   [mod."github.com/spf13/viper"]
     version = "v1.19.0"
     hash = "sha256-MZ8EAvdgpGbw6kmUz8UOaAAAMdPPGd14TrCBAY+A1T4="
```
