# [?] fix: prevent malicious peer DoS in block sync (#940)

## Summary
Severity: Unknown
Chain: Morph
Component: morph-l2/morph
Published: 2026-04-24
Source: https://github.com/morph-l2/morph/commit/78c30ab446bbe0cd1e7cd0adb74ccf3f312c5b04
Type: security-commit

## Details
fix: prevent malicious peer DoS in block sync (#940)

Co-authored-by: allen.wu <allen.wu@bitget.com>

## Patch
### Makefile
```diff
@@ -1,7 +1,7 @@
 ################## update dependencies ####################
 ETHEREUM_SUBMODULE_COMMIT_OR_TAG := morph-v2.2.1
 ETHEREUM_TARGET_VERSION := morph-v2.2.1
-TENDERMINT_TARGET_VERSION := v0.3.4
+TENDERMINT_TARGET_VERSION := v0.3.6
 
 
 ETHEREUM_MODULE_NAME := github.com/morph-l2/go-ethereum
```

### bindings/go.mod
```diff
@@ -2,7 +2,7 @@ module morph-l2/bindings
 
 go 1.24.0
 
-replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.4
+replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.6
 
 require github.com/morph-l2/go-ethereum v1.10.14-0.20260317041928-1d4605778e32
 
@@ -39,10 +39,10 @@ require (
 	github.com/tklauser/go-sysconf v0.3.13 // indirect
 	github.com/tklauser/numcpus v0.7.0 // indirect
 	github.com/yusufpapurcu/wmi v1.2.3 // indirect
-	golang.org/x/crypto v0.35.0 // indirect
-	golang.org/x/net v0.25.0 // indirect
-	golang.org/x/sync v0.11.0 // indirect
-	golang.org/x/sys v0.30.0 // indirect
+	golang.org/x/crypto v0.41.0 // indirect
+	golang.org/x/net v0.43.0 // indirect
+	golang.org/x/sync v0.16.0 // indirect
+	golang.org/x/sys v0.35.0 // indirect
 	gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce // indirect
 	rsc.io/tmplfunc v0.0.3 // indirect
 )
```

### bindings/go.sum
```diff
@@ -180,8 +180,8 @@ golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnf
 golang.org/x/crypto v0.0.0-20190308221718-c2843e01d9a2/go.mod h1:djNgcEr1/C05ACkg1iLfiJU5Ep61QUkGW8qpdssI0+w=
 golang.org/x/crypto v0.0.0-20191011191535-87dc89f01550/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
 golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
-golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
-golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
+golang.org/x/crypto v0.41.0 h1:WKYxWedPGCTVVl5+WHSSrOBT0O8lx32+zxmHxijgXp4=
+golang.org/x/crypto v0.41.0/go.mod h1:pO5AFd7FA68rFak7rOAGVuygIISepHftHnr8dr6+sUc=
 golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20181114220301-adae6a3d119a/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -192,15 +192,15 @@ golang.org/x/net v0.0.0-20201021035429-f5854403a974/go.mod h1:sp8m0HH+o8qH0wwXwY
 golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT/9KSuxbyM7479/AVlXFRxuMCk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.25.0 h1:d/OCCoBEUq33pjydKrGQhw7IlUPI2Oylr+8qLx49kac=
-golang.org/x/net v0.25.0/go.mod h1:JkAGAh7GEvH74S6FOH42FLoXpXbE/aqXSrIQjXgsiwM=
+golang.org/x/net v0.43.0 h1:lat02VYK2j4aLzMzecihNvTlJNQUq316m2Mr9rnM6YE=
+golang.org/x/net v0.43.0/go.mod h1:vhO1fvI4dGsIjh73sWfUVjj3N7CA9WkKJNQm2svM6Jg=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181108010431-42b317875d0f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181221193216-37e7f081c4d4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190423024810-112230192c58/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
-golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.16.0 h1:ycBJEhp9p4vXvUZNszeOq0kGTPghopOL8q0fq3vstxw=
+golang.org/x/sync v0.16.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180926160741-c2ed4eda69e7/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -223,16 +223,16 @@ golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
-golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.35.0 h1:vz1N37gP5bs89s7He8XuIYXpyY0+QlsKmzipCbUtyxI=
+golang.org/x/sys v0.35.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
-golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
+golang.org/x/text v0.28.0 h1:rhazDwis8INMIwQ4tpjLDzUhx6RlXqZNPEM0huQojng=
+golang.org/x/text v0.28.0/go.mod h1:U8nCwOR8jO/marOQ0QbDiOngZVEBB7MAiitBuMjXiNU=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20191119224855-298f0cb1881e/go.mod h1:b+2E5dAYhXwXZwtnZ6UAqBI28+e2cm9otk0dWdXHAEo=
 golang.org/x/tools v0.0.0-20201224043029-2b0845dc783e/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
```

### contracts/go.mod
```diff
@@ -2,7 +2,7 @@ module morph-l2/contract
 
 go 1.24.0
 
-replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.4
+replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.6
 
 require (
 	github.com/iden3/go-iden3-crypto v0.0.16
@@ -62,12 +62,12 @@ require (
 	github.com/tklauser/numcpus v0.7.0 // indirect
 	github.com/tyler-smith/go-bip39 v1.1.0 // indirect
 	github.com/yusufpapurcu/wmi v1.2.3 // indirect
-	golang.org/x/crypto v0.35.0 // indirect
-	golang.org/x/net v0.25.0 // indirect
-	golang.org/x/sync v0.11.0 // indirect
-	golang.org/x/sys v0.30.0 // indirect
-	golang.org/x/text v0.22.0 // indirect
-	golang.org/x/time v0.5.0 // indirect
+	golang.org/x/crypto v0.41.0 // indirect
+	golang.org/x/net v0.43.0 // indirect
+	golang.org/x/sync v0.16.0 // indirect
+	golang.org/x/sys v0.35.0 // indirect
+	golang.org/x/text v0.28.0 // indirect
+	golang.org/x/time v0.12.0 // indirect
 	gopkg.in/natefinch/lumberjack.v2 v2.2.1 // indirect
 	gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce // indirect
 	gopkg.in/urfave/cli.v1 v1.20.0 // indirect
```

### contracts/go.sum
```diff
@@ -215,8 +215,8 @@ golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnf
 golang.org/x/crypto v0.0.0-20190308221718-c2843e01d9a2/go.mod h1:djNgcEr1/C05ACkg1iLfiJU5Ep61QUkGW8qpdssI0+w=
 golang.org/x/crypto v0.0.0-20191011191535-87dc89f01550/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
 golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
-golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
-golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
+golang.org/x/crypto v0.41.0 h1:WKYxWedPGCTVVl5+WHSSrOBT0O8lx32+zxmHxijgXp4=
+golang.org/x/crypto v0.41.0/go.mod h1:pO5AFd7FA68rFak7rOAGVuygIISepHftHnr8dr6+sUc=
 golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20181114220301-adae6a3d119a/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -227,16 +227,16 @@ golang.org/x/net v0.0.0-20201021035429-f5854403a974/go.mod h1:sp8m0HH+o8qH0wwXwY
 golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT/9KSuxbyM7479/AVlXFRxuMCk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.25.0 h1:d/OCCoBEUq33pjydKrGQhw7IlUPI2Oylr+8qLx49kac=
-golang.org/x/net v0.25.0/go.mod h1:JkAGAh7GEvH74S6FOH42FLoXpXbE/aqXSrIQjXgsiwM=
+golang.org/x/net v0.43.0 h1:lat02VYK2j4aLzMzecihNvTlJNQUq316m2Mr9rnM6YE=
+golang.org/x/net v0.43.0/go.mod h1:vhO1fvI4dGsIjh73sWfUVjj3N7CA9WkKJNQm2svM6Jg=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181108010431-42b317875d0f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181221193216-37e7f081c4d4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190423024810-112230192c58/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
-golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.16.0 h1:ycBJEhp9p4vXvUZNszeOq0kGTPghopOL8q0fq3vstxw=
+golang.org/x/sync v0.16.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180926160741-c2ed4eda69e7/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -261,18 +261,18 @@ golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
-golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.35.0 h1:vz1N37gP5bs89s7He8XuIYXpyY0+QlsKmzipCbUtyxI=
+golang.org/x/sys v0.35.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
-golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
-golang.org/x/time v0.5.0 h1:o7cqy6amK/52YcAKIPlM3a+Fpj35zvRj2TP+e1xFSfk=
-golang.org/x/time v0.5.0/go.mod h1:3BpzKBy/shNhVucY/MWOyx10tF3SFh9QdLuxbVysPQM=
+golang.org/x/text v0.28.0 h1:rhazDwis8INMIwQ4tpjLDzUhx6RlXqZNPEM0huQojng=
+golang.org/x/text v0.28.0/go.mod h1:U8nCwOR8jO/marOQ0QbDiOngZVEBB7MAiitBuMjXiNU=
+golang.org/x/time v0.12.0 h1:ScB/8o8olJvc+CQPWrK3fPZNfh7qgwCrY0zJmoEQLSE=
+golang.org/x/time v0.12.0/go.mod h1:CDIdPxbZBQxdj6cxyCIdrNogrJKMJ7pr37NYpMcMDSg=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20191119224855-298f0cb1881e/go.mod h1:b+2E5dAYhXwXZwtnZ6UAqBI28+e2cm9otk0dWdXHAEo=
 golang.org/x/tools v0.0.0-20201224043029-2b0845dc783e/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
```

### node/go.mod
```diff
@@ -2,7 +2,7 @@ module morph-l2/node
 
 go 1.24.0
 
-replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.4
+replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.6
 
 require (
 	github.com/cenkalti/backoff/v4 v4.1.3
@@ -18,7 +18,6 @@ require (
 	github.com/syndtr/goleveldb v1.0.1-0.20220614013038-64ee5596c38a
 	github.com/tendermint/tendermint v0.35.9
 	github.com/urfave/cli v1.22.17
-	golang.org/x/exp v0.0.0-20230905200255-921286631fa9
 	gopkg.in/natefinch/lumberjack.v2 v2.2.1
 )
 
@@ -115,12 +114,12 @@ require (
 	github.com/tyler-smith/go-bip39 v1.1.0 // indirect
 	github.com/yusufpapurcu/wmi v1.2.3 // indirect
 	go.etcd.io/bbolt v1.3.9 // indirect
-	golang.org/x/crypto v0.35.0 // indirect
-	golang.org/x/net v0.25.0 // indirect
-	golang.org/x/sync v0.11.0 // indirect
-	golang.org/x/sys v0.30.0 // indirect
-	golang.org/x/text v0.22.0 // indirect
-	golang.org/x/time v0.5.0 // indirect
+	golang.org/x/crypto v0.41.0 // indirect
+	golang.org/x/net v0.43.0 // indirect
+	golang.org/x/sync v0.16.0 // indirect
+	golang.org/x/sys v0.35.0 // indirect
+	golang.org/x/text v0.28.0 // indirect
+	golang.org/x/time v0.12.0 // indirect
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20240123012728-ef4313101c80 // indirect
 	google.golang.org/grpc v1.62.1 // indirect
 	google.golang.org/protobuf v1.33.0 // indirect
```

### node/go.sum
```diff
@@ -363,8 +363,8 @@ github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd/go.mod h1:6dJ
 github.com/modern-go/reflect2 v1.0.1/go.mod h1:bx2lNnkwVCuqBIxFjflWJWanXIb3RllmbCylyMrvgv0=
 github.com/morph-l2/go-ethereum v1.10.14-0.20260317041928-1d4605778e32 h1:nWcBwsUNXJvC8rmnX4zoRAwZmXQDDawoS+aTC2nqG3g=
 github.com/morph-l2/go-ethereum v1.10.14-0.20260317041928-1d4605778e32/go.mod h1:nkVzHjQWCOjvukQW8ittlwX+Xz9gmVHrP7mUi7zoHTs=
-github.com/morph-l2/tendermint v0.3.4 h1:GxYs6XY/koPmJDRwhELr5s5V53m/yhO27+DeL6bjUBg=
-github.com/morph-l2/tendermint v0.3.4/go.mod h1:TtCzp9l6Z6yDUiwv3TbqKqw8Q8RKp3fSz5+adO1/Y8w=
+github.com/morph-l2/tendermint v0.3.6 h1:N9FWdbAV7PSBifnCnVXgMUj9jKHMITNdrPniB8hiXlQ=
+github.com/morph-l2/tendermint v0.3.6/go.mod h1:TtCzp9l6Z6yDUiwv3TbqKqw8Q8RKp3fSz5+adO1/Y8w=
 github.com/mwitkow/go-conntrack v0.0.0-20161129095857-cc309e4a2223/go.mod h1:qRWi+5nqEBWmkhHvq77mSJWrCKwh8bxhgT7d/eI7P4U=
 github.com/nxadm/tail v1.4.4/go.mod h1:kenIhsEOeOJmVchQTgglprH7qJGnHDVpk1VPCcaMI8A=
 github.com/nxadm/tail v1.4.8 h1:nPr65rt6Y5JFSKQO7qToXr7pePgD6Gwiw05lkbyAQTE=
@@ -537,8 +537,8 @@ golang.org/x/crypto v0.0.0-20191011191535-87dc89f01550/go.mod h1:yigFU9vqHzYiE8U
 golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210421170649-83a5a9bb288b/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20220722155217-630584e8d5aa/go.mod h1:IxCIyHEi3zRg3s0A5j5BB6A9Jmi73HwBIUl50j+osU4=
-golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
-golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
+golang.org/x/crypto v0.41.0 h1:WKYxWedPGCTVVl5+WHSSrOBT0O8lx32+zxmHxijgXp4=
+golang.org/x/crypto v0.41.0/go.mod h1:pO5AFd7FA68rFak7rOAGVuygIISepHftHnr8dr6+sUc=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190306152737-a1d7652674e8/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190510132918-efd6b22b2522/go.mod h1:ZjyILWgesfNpC6sMxTJOJm9Kp84zZh5NQWvqDGG3Qr8=
@@ -549,8 +549,6 @@ golang.org/x/exp v0.0.0-20191227195350-da58074b4299/go.mod h1:2RIsYlXP63K8oxa1u0
 golang.org/x/exp v0.0.0-20200119233911-0405dc783f0a/go.mod h1:2RIsYlXP63K8oxa1u096TMicItID8zy7Y6sNkU49FU4=
 golang.org/x/exp v0.0.0-20200207192155-f17229e696bd/go.mod h1:J/WKrq2StrnmMY6+EHIKF9dgMWnmCNThgcyBT1FY9mM=
 golang.org/x/exp v0.0.0-20200224162631-6cc2880d07d6/go.mod h1:3jZMyOhIsHpP37uCMkUooju7aAi5cS1Q23tOzKc+0MU=
-golang.org/x/exp v0.0.0-20230905200255-921286631fa9 h1:GoHiUyI/Tp2nVkLI2mCxVkOjsbSXD66ic0XW0js0R9g=
-golang.org/x/exp v0.0.0-20230905200255-921286631fa9/go.mod h1:S2oDrQGGwySpoQPVqRShND87VCbxmc6bL1Yd2oYrm6k=
 golang.org/x/image v0.0.0-20190227222117-0694c2d4d067/go.mod h1:kZ7UVZpmo3dzQBMxlp+ypCbDeSB+sBbTgSJuh5dn5js=
 golang.org/x/image v0.0.0-20190802002840-cff245a6509b/go.mod h1:FeLwcggjj3mMvU+oOTbSwawSJRM1uh48EjtB4UJZlP0=
 golang.org/x/lint v0.0.0-20181026193005-c67002cb31c3/go.mod h1:UVdnD1Gm6xHRNCYTkRU2/jEulfH38KcIWyp/GAMgvoE=
@@ -574,8 +572,8 @@ golang.org/x/mod v0.2.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
-golang.org/x/mod v0.17.0 h1:zY54UmvipHiNd+pm+m0x9KhZ9hl1/7QNMyxXbc6ICqA=
-golang.org/x/mod v0.17.0/go.mod h1:hTbmBsO62+eylJbnUtE2MGJUyE7QWk4xUqPFrRgJ+7c=
+golang.org/x/mod v0.26.0 h1:EGMPT//Ezu+ylkCijjPc+f4Aih7sZvaAr+O3EHBxvZg=
+golang.org/x/mod v0.26.0/go.mod h1:/j6NAhSk8iQ723BGAUyoAcn7SlD7s15Dp9Nd/SfeaFQ=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -615,8 +613,8 @@ golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT
 golang.org/x/net v0.0.0-20211112202133-69e39bad7dc2/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.25.0 h1:d/OCCoBEUq33pjydKrGQhw7IlUPI2Oylr+8qLx49kac=
-golang.org/x/net v0.25.0/go.mod h1:JkAGAh7GEvH74S6FOH42FLoXpXbE/aqXSrIQjXgsiwM=
+golang.org/x/net v0.43.0 h1:lat02VYK2j4aLzMzecihNvTlJNQUq316m2Mr9rnM6YE=
+golang.org/x/net v0.43.0/go.mod h1:vhO1fvI4dGsIjh73sWfUVjj3N7CA9WkKJNQm2svM6Jg=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20190226205417-e64efc72b421/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.0.0-20190604053449-0f29369cfe45/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
@@ -637,8 +635,8 @@ golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
-golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.16.0 h1:ycBJEhp9p4vXvUZNszeOq0kGTPghopOL8q0fq3vstxw=
+golang.org/x/sync v0.16.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -697,8 +695,8 @@ golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
-golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.35.0 h1:vz1N37gP5bs89s7He8XuIYXpyY0+QlsKmzipCbUtyxI=
+golang.org/x/sys v0.35.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -709,13 +707,13 @@ golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
-golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
+golang.org/x/text v0.28.0 h1:rhazDwis8INMIwQ4tpjLDzUhx6RlXqZNPEM0huQojng=
+golang.org/x/text v0.28.0/go.mod h1:U8nCwOR8jO/marOQ0QbDiOngZVEBB7MAiitBuMjXiNU=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20191024005414-555d28b269f0/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
-golang.org/x/time v0.5.0 h1:o7cqy6amK/52YcAKIPlM3a+Fpj35zvRj2TP+e1xFSfk=
-golang.org/x/time v0.5.0/go.mod h1:3BpzKBy/shNhVucY/MWOyx10tF3SFh9QdLuxbVysPQM=
+golang.org/x/time v0.12.0 h1:ScB/8o8olJvc+CQPWrK3fPZNfh7qgwCrY0zJmoEQLSE=
+golang.org/x/time v0.12.0/go.mod h1:CDIdPxbZBQxdj6cxyCIdrNogrJKMJ7pr37NYpMcMDSg=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20190114222345-bf090417da8b/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20190226205152-f727befe758c/go.mod h1:9Yl7xja0Znq3iFh3HoIrodX9oNMXvdceNzlUR8zjMvY=
@@ -766,8 +764,8 @@ golang.org/x/tools v0.0.0-20210105154028-b0ab187a4818/go.mod h1:emZCQorbCU4vsT4f
 golang.org/x/tools v0.0.0-20210106214847-113979e3529a/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
 golang.org/x/tools v0.0.0-20210108195828-e2f9c7f1fc8e/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
 golang.org/x/tools v0.1.0/go.mod h1:xkSsbof2nBLbhDlRMhhhyNLN/zl3eTqcnHD5viDpcZ0=
-golang.org/x/tools v0.21.1-0.20240508182429-e35e4ccd0d2d h1:vU5i/LfpvrRCpgM/VPfJLg5KjxD3E+hfT1SH+d9zLwg=
-golang.org/x/tools v0.21.1-0.20240508182429-e35e4ccd0d2d/go.mod h1:aiJjzUbINMkxbQROHiO6hDPo2LHcIPhhQsa9DLh0yGk=
+golang.org/x/tools v0.35.0 h1:mBffYraMEf7aa0sB+NuKnuCy8qI/9Bughn8dC2Gu5r0=
+golang.org/x/tools v0.35.0/go.mod h1:NKdj5HkL/73byiZSJjqJgKn3ep7KjFkBOkR/Hps3VPw=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
```

### ops/l2-genesis/go.mod
```diff
@@ -2,7 +2,7 @@ module morph-l2/morph-deployer
 
 go 1.24.0
 
-replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.4
+replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.6
 
 require (
 	github.com/holiman/uint256 v1.2.4
@@ -65,12 +65,12 @@ require (
 	github.com/tklauser/numcpus v0.7.0 // indirect
 	github.com/tyler-smith/go-bip39 v1.1.0 // indirect
 	github.com/yusufpapurcu/wmi v1.2.3 // indirect
-	golang.org/x/crypto v0.35.0 // indirect
-	golang.org/x/net v0.25.0 // indirect
-	golang.org/x/sync v0.11.0 // indirect
-	golang.org/x/sys v0.30.0 // indirect
-	golang.org/x/text v0.22.0 // indirect
-	golang.org/x/time v0.5.0 // indirect
+	golang.org/x/crypto v0.41.0 // indirect
+	golang.org/x/net v0.43.0 // indirect
+	golang.org/x/sync v0.16.0 // indirect
+	golang.org/x/sys v0.35.0 // indirect
+	golang.org/x/text v0.28.0 // indirect
+	golang.org/x/time v0.12.0 // indirect
 	gopkg.in/natefinch/lumberjack.v2 v2.2.1 // indirect
 	gopkg.in/natefinch/npipe.v2 v2.0.0-20160621034901-c1b8fa8bdcce // indirect
 	gopkg.in/urfave/cli.v1 v1.20.0 // indirect
```

### ops/l2-genesis/go.sum
```diff
@@ -228,8 +228,8 @@ golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnf
 golang.org/x/crypto v0.0.0-20190308221718-c2843e01d9a2/go.mod h1:djNgcEr1/C05ACkg1iLfiJU5Ep61QUkGW8qpdssI0+w=
 golang.org/x/crypto v0.0.0-20191011191535-87dc89f01550/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
 golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
-golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
-golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
+golang.org/x/crypto v0.41.0 h1:WKYxWedPGCTVVl5+WHSSrOBT0O8lx32+zxmHxijgXp4=
+golang.org/x/crypto v0.41.0/go.mod h1:pO5AFd7FA68rFak7rOAGVuygIISepHftHnr8dr6+sUc=
 golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20181114220301-adae6a3d119a/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -240,16 +240,16 @@ golang.org/x/net v0.0.0-20201021035429-f5854403a974/go.mod h1:sp8m0HH+o8qH0wwXwY
 golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT/9KSuxbyM7479/AVlXFRxuMCk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.25.0 h1:d/OCCoBEUq33pjydKrGQhw7IlUPI2Oylr+8qLx49kac=
-golang.org/x/net v0.25.0/go.mod h1:JkAGAh7GEvH74S6FOH42FLoXpXbE/aqXSrIQjXgsiwM=
+golang.org/x/net v0.43.0 h1:lat02VYK2j4aLzMzecihNvTlJNQUq316m2Mr9rnM6YE=
+golang.org/x/net v0.43.0/go.mod h1:vhO1fvI4dGsIjh73sWfUVjj3N7CA9WkKJNQm2svM6Jg=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181108010431-42b317875d0f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181221193216-37e7f081c4d4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190423024810-112230192c58/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
-golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.16.0 h1:ycBJEhp9p4vXvUZNszeOq0kGTPghopOL8q0fq3vstxw=
+golang.org/x/sync v0.16.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180926160741-c2ed4eda69e7/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -274,18 +274,18 @@ golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
-golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.35.0 h1:vz1N37gP5bs89s7He8XuIYXpyY0+QlsKmzipCbUtyxI=
+golang.org/x/sys v0.35.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
-golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
-golang.org/x/time v0.5.0 h1:o7cqy6amK/52YcAKIPlM3a+Fpj35zvRj2TP+e1xFSfk=
-golang.org/x/time v0.5.0/go.mod h1:3BpzKBy/shNhVucY/MWOyx10tF3SFh9QdLuxbVysPQM=
+golang.org/x/text v0.28.0 h1:rhazDwis8INMIwQ4tpjLDzUhx6RlXqZNPEM0huQojng=
+golang.org/x/text v0.28.0/go.mod h1:U8nCwOR8jO/marOQ0QbDiOngZVEBB7MAiitBuMjXiNU=
+golang.org/x/time v0.12.0 h1:ScB/8o8olJvc+CQPWrK3fPZNfh7qgwCrY0zJmoEQLSE=
+golang.org/x/time v0.12.0/go.mod h1:CDIdPxbZBQxdj6cxyCIdrNogrJKMJ7pr37NYpMcMDSg=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20191119224855-298f0cb1881e/go.mod h1:b+2E5dAYhXwXZwtnZ6UAqBI28+e2cm9otk0dWdXHAEo=
 golang.org/x/tools v0.0.0-20201224043029-2b0845dc783e/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
```

### ops/tools/go.mod
```diff
@@ -2,7 +2,7 @@ module morph-l2/tools
 
 go 1.24.0
 
-replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.4
+replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.6
 
 require (
 	github.com/morph-l2/go-ethereum v1.10.14-0.20260317041928-1d4605778e32
@@ -75,12 +75,12 @@ require (
 	github.com/tklauser/numcpus v0.7.0 // indirect
 	github.com/tyler-smith/go-bip39 v1.1.0 // indirect
 	github.com/yusufpapurcu/wmi v1.2.3 // indirect
-	golang.org/x/crypto v0.35.0 // indirect
-	golang.org/x/net v0.25.0 // indirect
-	golang.org/x/sync v0.11.0 // indirect
-	golang.org/x/sys v0.30.0 // indirect
-	golang.org/x/text v0.22.0 // indirect
-	golang.org/x/time v0.5.0 // indirect
+	golang.org/x/crypto v0.41.0 // indirect
+	golang.org/x/net v0.43.0 // indirect
+	golang.org/x/sync v0.16.0 // indirect
+	golang.org/x/sys v0.35.0 // indirect
+	golang.org/x/text v0.28.0 // indirect
+	golang.org/x/time v0.12.0 // indirect
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20240123012728-ef4313101c80 // indirect
 	google.golang.org/grpc v1.62.1 // indirect
 	google.golang.org/protobuf v1.33.0 // indirect
```

### ops/tools/go.sum
```diff
@@ -165,8 +165,8 @@ github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd/go.mod h1:6dJ
 github.com/modern-go/reflect2 v1.0.1/go.mod h1:bx2lNnkwVCuqBIxFjflWJWanXIb3RllmbCylyMrvgv0=
 github.com/morph-l2/go-ethereum v1.10.14-0.20260317041928-1d4605778e32 h1:nWcBwsUNXJvC8rmnX4zoRAwZmXQDDawoS+aTC2nqG3g=
 github.com/morph-l2/go-ethereum v1.10.14-0.20260317041928-1d4605778e32/go.mod h1:nkVzHjQWCOjvukQW8ittlwX+Xz9gmVHrP7mUi7zoHTs=
-github.com/morph-l2/tendermint v0.3.4 h1:GxYs6XY/koPmJDRwhELr5s5V53m/yhO27+DeL6bjUBg=
-github.com/morph-l2/tendermint v0.3.4/go.mod h1:TtCzp9l6Z6yDUiwv3TbqKqw8Q8RKp3fSz5+adO1/Y8w=
+github.com/morph-l2/tendermint v0.3.6 h1:N9FWdbAV7PSBifnCnVXgMUj9jKHMITNdrPniB8hiXlQ=
+github.com/morph-l2/tendermint v0.3.6/go.mod h1:TtCzp9l6Z6yDUiwv3TbqKqw8Q8RKp3fSz5+adO1/Y8w=
 github.com/mwitkow/go-conntrack v0.0.0-20161129095857-cc309e4a2223/go.mod h1:qRWi+5nqEBWmkhHvq77mSJWrCKwh8bxhgT7d/eI7P4U=
 github.com/nxadm/tail v1.4.4/go.mod h1:kenIhsEOeOJmVchQTgglprH7qJGnHDVpk1VPCcaMI8A=
 github.com/nxadm/tail v1.4.8 h1:nPr65rt6Y5JFSKQO7qToXr7pePgD6Gwiw05lkbyAQTE=
@@ -253,8 +253,8 @@ golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnf
 golang.org/x/crypto v0.0.0-20190308221718-c2843e01d9a2/go.mod h1:djNgcEr1/C05ACkg1iLfiJU5Ep61QUkGW8qpdssI0+w=
 golang.org/x/crypto v0.0.0-20191011191535-87dc89f01550/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
 golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
-golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
-golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
+golang.org/x/crypto v0.41.0 h1:WKYxWedPGCTVVl5+WHSSrOBT0O8lx32+zxmHxijgXp4=
+golang.org/x/crypto v0.41.0/go.mod h1:pO5AFd7FA68rFak7rOAGVuygIISepHftHnr8dr6+sUc=
 golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20181114220301-adae6a3d119a/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -265,16 +265,16 @@ golang.org/x/net v0.0.0-20201021035429-f5854403a974/go.mod h1:sp8m0HH+o8qH0wwXwY
 golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT/9KSuxbyM7479/AVlXFRxuMCk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.25.0 h1:d/OCCoBEUq33pjydKrGQhw7IlUPI2Oylr+8qLx49kac=
-golang.org/x/net v0.25.0/go.mod h1:JkAGAh7GEvH74S6FOH42FLoXpXbE/aqXSrIQjXgsiwM=
+golang.org/x/net v0.43.0 h1:lat02VYK2j4aLzMzecihNvTlJNQUq316m2Mr9rnM6YE=
+golang.org/x/net v0.43.0/go.mod h1:vhO1fvI4dGsIjh73sWfUVjj3N7CA9WkKJNQm2svM6Jg=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181108010431-42b317875d0f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20181221193216-37e7f081c4d4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190423024810-112230192c58/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
-golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.16.0 h1:ycBJEhp9p4vXvUZNszeOq0kGTPghopOL8q0fq3vstxw=
+golang.org/x/sync v0.16.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180926160741-c2ed4eda69e7/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -299,18 +299,18 @@ golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
-golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.35.0 h1:vz1N37gP5bs89s7He8XuIYXpyY0+QlsKmzipCbUtyxI=
+golang.org/x/sys v0.35.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
-golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
-golang.org/x/time v0.5.0 h1:o7cqy6amK/52YcAKIPlM3a+Fpj35zvRj2TP+e1xFSfk=
-golang.org/x/time v0.5.0/go.mod h1:3BpzKBy/shNhVucY/MWOyx10tF3SFh9QdLuxbVysPQM=
+golang.org/x/text v0.28.0 h1:rhazDwis8INMIwQ4tpjLDzUhx6RlXqZNPEM0huQojng=
+golang.org/x/text v0.28.0/go.mod h1:U8nCwOR8jO/marOQ0QbDiOngZVEBB7MAiitBuMjXiNU=
+golang.org/x/time v0.12.0 h1:ScB/8o8olJvc+CQPWrK3fPZNfh7qgwCrY0zJmoEQLSE=
+golang.org/x/time v0.12.0/go.mod h1:CDIdPxbZBQxdj6cxyCIdrNogrJKMJ7pr37NYpMcMDSg=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20191119224855-298f0cb1881e/go.mod h1:b+2E5dAYhXwXZwtnZ6UAqBI28+e2cm9otk0dWdXHAEo=
 golang.org/x/tools v0.0.0-20201224043029-2b0845dc783e/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
```

### oracle/go.mod
```diff
@@ -2,7 +2,7 @@ module morph-l2/oracle
 
 go 1.24.0
 
-replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.4
+replace github.com/tendermint/tendermint => github.com/morph-l2/tendermint v0.3.6
 
 require (
 	github.com/go-kit/kit v0.12.0
@@ -36,7 +36,7 @@ require (
 	github.com/go-kit/log v0.2.1 // indirect
 	github.com/go-logfmt/logfmt v0.6.0 // indirect
 	github.com/go-ole/go-ole v1.3.0 // indirect
-	github.com/go-resty/resty/v2 v2.13.1 // indirect
+	github.com/go-resty/resty/v2 v2.17.2 // indirect
 	github.com/go-stack/stack v1.8.1 // indirect
 	github.com/golang-jwt/jwt/v4 v4.5.0 // indirect
 	github.com/golang/protobuf v1.5.3 // indirect
@@ -83,12 +83,12 @@ require (
 	github.com/tklauser/numcpus v0.7.0 // indirect
 	github.com/tyler-smith/go-bip39 v1.1.0 // indirect
 	github.com/yusufpapurcu/wmi v1.2.3 // indirect
-	golang.org/x/crypto v0.35.0 // indirect
-	golang.org/x/net v0.25.0 // indirect
-	golang.org/x/sync v0.11.0 // indirect
-	golang.org/x/sys v0.30.0 // indirect
-	golang.org/x/text v0.22.0 // indirect
-	golang.org/x/time v0.5.0 // indirect
+	golang.org/x/crypto v0.41.0 // indirect
+	golang.org/x/net v0.43.0 // indirect
+	golang.org/x/sync v0.16.0 // indirect
+	golang.org/x/sys v0.35.0 // indirect
+	golang.org/x/text v0.28.0 // indirect
+	golang.org/x/time v0.12.0 // indirect
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20240123012728-ef4313101c80 // indirect
 	google.golang.org/grpc v1.62.1 // indirect
 	google.golang.org/protobuf v1.33.0 // indirect
```
