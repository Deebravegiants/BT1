# [?] go.mod: update crypto to solve CVE-2025-22869 (#2948)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2025-03-12
Source: https://github.com/bnb-chain/bsc/commit/09e56d9ed5958e0b2a917e379afffb277e88e1b9
Type: security-commit

## Details
go.mod: update crypto to solve CVE-2025-22869 (#2948)

## Patch
### go.mod
```diff
@@ -1,6 +1,6 @@
 module github.com/ethereum/go-ethereum
 
-go 1.22.0
+go 1.23.0
 
 require (
 	github.com/Azure/azure-sdk-for-go/sdk/storage/azblob v1.2.0
@@ -79,11 +79,11 @@ require (
 	github.com/wealdtech/go-eth2-wallet-encryptor-keystorev4 v1.1.3
 	github.com/willf/bitset v1.1.3
 	go.uber.org/automaxprocs v1.5.2
-	golang.org/x/crypto v0.32.0
+	golang.org/x/crypto v0.35.0
 	golang.org/x/exp v0.0.0-20241217172543-b2144cdd0a67
-	golang.org/x/sync v0.10.0
-	golang.org/x/sys v0.29.0
-	golang.org/x/text v0.21.0
+	golang.org/x/sync v0.11.0
+	golang.org/x/sys v0.30.0
+	golang.org/x/text v0.22.0
 	golang.org/x/time v0.5.0
 	golang.org/x/tools v0.29.0
 	google.golang.org/protobuf v1.36.0
@@ -297,7 +297,7 @@ require (
 	golang.org/x/mod v0.22.0 // indirect
 	golang.org/x/net v0.34.0 // indirect
 	golang.org/x/oauth2 v0.24.0 // indirect
-	golang.org/x/term v0.28.0 // indirect
+	golang.org/x/term v0.29.0 // indirect
 	google.golang.org/api v0.44.0 // indirect
 	google.golang.org/genproto v0.0.0-20231016165738-49dd2c1f3d0b // indirect
 	google.golang.org/genproto/googleapis/api v0.0.0-20231012201019-e917dd12ba7a // indirect
```

### go.sum
```diff
@@ -1292,8 +1292,8 @@ golang.org/x/crypto v0.0.0-20220722155217-630584e8d5aa/go.mod h1:IxCIyHEi3zRg3s0
 golang.org/x/crypto v0.8.0/go.mod h1:mRqEX+O9/h5TFCrQhkgjo2yKi0yYA+9ecGkdQoHrywE=
 golang.org/x/crypto v0.12.0/go.mod h1:NF0Gs7EO5K4qLn+Ylc+fih8BSTeIjAP05siRnAh98yw=
 golang.org/x/crypto v0.18.0/go.mod h1:R0j02AL6hcrfOiy9T4ZYp/rcWeMxM3L6QYxlOuEG1mg=
-golang.org/x/crypto v0.32.0 h1:euUpcYgM8WcP71gNpTqQCn6rC2t6ULUPiOzfWaXVVfc=
-golang.org/x/crypto v0.32.0/go.mod h1:ZnnJkOaASj8g0AjIduWNlq2NRxL0PlBrbKVyZ6V/Ugc=
+golang.org/x/crypto v0.35.0 h1:b15kiHdrGCHrP6LvwaQ3c03kgNhhiMgvlhxHQhmg2Xs=
+golang.org/x/crypto v0.35.0/go.mod h1:dy7dXNW32cAb/6/PRuTNsix8T+vJAqvuIy5Bli/x0YQ=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190306152737-a1d7652674e8/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190510132918-efd6b22b2522/go.mod h1:ZjyILWgesfNpC6sMxTJOJm9Kp84zZh5NQWvqDGG3Qr8=
@@ -1423,8 +1423,8 @@ golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.1.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.10.0 h1:3NQrjDixjgGwUOCaF8w2+VYHv0Ve/vGYSbdkTa98gmQ=
-golang.org/x/sync v0.10.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.11.0 h1:GGz8+XQP4FvTTrjZPzNKTMFtSXH80RAzG+5ghFPgK9w=
+golang.org/x/sync v0.11.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
 golang.org/x/sys v0.0.0-20180810173357-98c5dad5d1a0/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -1519,8 +1519,8 @@ golang.org/x/sys v0.9.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.11.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.14.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/sys v0.16.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.29.0 h1:TPYlXGxvx1MGTn2GiZDhnjPA9wZzZeGKHHmKhHYvgaU=
-golang.org/x/sys v0.29.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/sys v0.30.0 h1:QjkSwP/36a20jFYWkSue1YwXzLmsV5Gfq7Eiy72C1uc=
+golang.org/x/sys v0.30.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/term v0.0.0-20201117132131-f5c789dd3221/go.mod h1:Nr5EML6q2oocZ2LXRh80K7BxOlk5/8JxuGnuhpl+muw=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
@@ -1529,8 +1529,8 @@ golang.org/x/term v0.7.0/go.mod h1:P32HKFT3hSsZrRxla30E9HqToFYAQPCMs/zFMBUFqPY=
 golang.org/x/term v0.8.0/go.mod h1:xPskH00ivmX89bAKVGSKKtLOWNx2+17Eiy94tnKShWo=
 golang.org/x/term v0.11.0/go.mod h1:zC9APTIj3jG3FdV/Ons+XE1riIZXG4aZ4GTHiPZJPIU=
 golang.org/x/term v0.16.0/go.mod h1:yn7UURbUtPyrVJPGPq404EukNFxcm/foM+bV/bfcDsY=
-golang.org/x/term v0.28.0 h1:/Ts8HFuMR2E6IP/jlo7QVLZHggjKQbhu/7H0LJFr3Gg=
-golang.org/x/term v0.28.0/go.mod h1:Sw/lC2IAUZ92udQNf3WodGtn4k/XoLyZoh8v/8uiwek=
+golang.org/x/term v0.29.0 h1:L6pJp37ocefwRRtYPKSWOWzOtWSxVajvz2ldH/xi3iU=
+golang.org/x/term v0.29.0/go.mod h1:6bl4lRlvVuDgSf3179VpIxBF0o10JUpXWOnI7nErv7s=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.1-0.20180807135948-17ff2d5776d2/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1545,8 +1545,8 @@ golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/text v0.9.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/text v0.12.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
 golang.org/x/text v0.14.0/go.mod h1:18ZOQIKpY8NJVqYksKHtTdi31H5itFRjB5/qKTNYzSU=
-golang.org/x/text v0.21.0 h1:zyQAAkrwaneQ066sspRyJaG9VNi/YJ1NfzcGB3hZ/qo=
-golang.org/x/text v0.21.0/go.mod h1:4IBbMaMmOPCJ8SecivzSH54+73PCFmPWxNTLm+vZkEQ=
+golang.org/x/text v0.22.0 h1:bofq7m3/HAFvbF51jz3Q9wLg3jkvSPuiZu/pD1XwgtM=
+golang.org/x/text v0.22.0/go.mod h1:YRoo4H8PVmsu+E3Ou7cqLVH8oXWIHVoX0jqUWALQhfY=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
```
