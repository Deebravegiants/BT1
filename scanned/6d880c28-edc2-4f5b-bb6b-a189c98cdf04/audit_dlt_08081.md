# [?] Updated github.com/btcsuite/btcd to address CVE-2024-34478

## Summary
Severity: Unknown
Chain: Bitcoin
Component: btcsuite/btcd
Published: 2024-08-15
Source: https://github.com/btcsuite/btcd/commit/913f95b2b258afac7b0139c4a1bef9f7e3c5bddc
Type: security-commit

## Details
Updated github.com/btcsuite/btcd to address CVE-2024-34478

synchronize dependencies

## Patch
### btcutil/go.mod
```diff
@@ -4,7 +4,7 @@ go 1.16
 
 require (
 	github.com/aead/siphash v1.0.1
-	github.com/btcsuite/btcd v0.23.5-0.20231215221805-96c9fd8078fd
+	github.com/btcsuite/btcd v0.24.2
 	github.com/btcsuite/btcd/btcec/v2 v2.1.3
 	github.com/btcsuite/btcd/chaincfg/chainhash v1.1.0
 	github.com/davecgh/go-spew v1.1.1
```

### btcutil/go.sum
```diff
@@ -2,13 +2,15 @@ github.com/aead/siphash v1.0.1 h1:FwHfE/T45KPKYuuSAKyyvE+oPWcaQ+CUmFW0bPlM+kg=
 github.com/aead/siphash v1.0.1/go.mod h1:Nywa3cDsYNNK3gaciGTWPwHt0wlpNV15vwmswBAUSII=
 github.com/btcsuite/btcd v0.20.1-beta/go.mod h1:wVuoA8VJLEcwgqHBwHmzLRazpKxTv13Px/pDuV7OomQ=
 github.com/btcsuite/btcd v0.22.0-beta.0.20220111032746-97732e52810c/go.mod h1:tjmYdS6MLJ5/s0Fj4DbLgSbDHbEqLJrtnHecBFkdz5M=
-github.com/btcsuite/btcd v0.23.5-0.20231215221805-96c9fd8078fd h1:js1gPwhcFflTZ7Nzl7WHaOTlTr5hIrR4n1NM4v9n4Kw=
 github.com/btcsuite/btcd v0.23.5-0.20231215221805-96c9fd8078fd/go.mod h1:nm3Bko6zh6bWP60UxwoT5LzdGJsQJaPo6HjduXq9p6A=
+github.com/btcsuite/btcd v0.24.2 h1:aLmxPguqxza+4ag8R1I2nnJjSu2iFn/kqtHTIImswcY=
+github.com/btcsuite/btcd v0.24.2/go.mod h1:5C8ChTkl5ejr3WHj8tkQSCmydiMEPB0ZhQhehpq7Dgg=
 github.com/btcsuite/btcd/btcec/v2 v2.1.0/go.mod h1:2VzYrv4Gm4apmbVVsSq5bqf1Ec8v56E48Vt0Y/umPgA=
 github.com/btcsuite/btcd/btcec/v2 v2.1.3 h1:xM/n3yIhHAhHy04z4i43C8p4ehixJZMsnrVJkgl+MTE=
 github.com/btcsuite/btcd/btcec/v2 v2.1.3/go.mod h1:ctjw4H1kknNJmRN4iP1R7bTQ+v3GJkZBd6mui8ZsAZE=
 github.com/btcsuite/btcd/btcutil v1.0.0/go.mod h1:Uoxwv0pqYWhD//tfTiipkxNfdhG9UrLwaeswfjfdF0A=
 github.com/btcsuite/btcd/btcutil v1.1.0/go.mod h1:5OapHB7A2hBBWLm48mmw4MOHNJCcUBTwmWH/0Jn8VHE=
+github.com/btcsuite/btcd/btcutil v1.1.5/go.mod h1:PSZZ4UitpLBWzxGd5VGOrLnmOjtPP/a6HaFo12zMs00=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.0/go.mod h1:7SFka0XMvUgj3hfZtydOrQY2mwhPclbT2snogU7SQQc=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1/go.mod h1:7SFka0XMvUgj3hfZtydOrQY2mwhPclbT2snogU7SQQc=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.1.0 h1:59Kx4K6lzOW5w6nFlA0v5+lk/6sjybR934QNHSJZPTQ=
@@ -65,8 +67,13 @@ github.com/onsi/gomega v1.10.1/go.mod h1:iN09h71vgCQne3DLsj+A5owkum+a2tYe+TOCB1y
 github.com/pmezard/go-difflib v1.0.0 h1:4DBwDE0NGyQoBHbLQYPwSUPoCMWR5BEzIk/f1lZbAQM=
 github.com/pmezard/go-difflib v1.0.0/go.mod h1:iKH77koFhYxTK1pcRnkKkqfTogsbg7gZNVY4sRDYZ/4=
 github.com/stretchr/objx v0.1.0/go.mod h1:HFkY916IF+rwdDfMAkV7OtwuqBVzrE8GR6GFx+wExME=
-github.com/stretchr/testify v1.7.0 h1:nwc3DEeHmmLAfoZucVR881uASk0Mfjw8xYJ99tb5CcY=
+github.com/stretchr/objx v0.4.0/go.mod h1:YvHI0jy2hoMjB+UWwv71VJQ9isScKT/TqJzVSSt89Yw=
+github.com/stretchr/objx v0.5.0/go.mod h1:Yh+to48EsGEfYuaHDzXPcE3xhTkx73EhmCGUpEOglKo=
 github.com/stretchr/testify v1.7.0/go.mod h1:6Fq8oRcR53rry900zMqJjRRixrwX3KX962/h/Wwjteg=
+github.com/stretchr/testify v1.7.1/go.mod h1:6Fq8oRcR53rry900zMqJjRRixrwX3KX962/h/Wwjteg=
+github.com/stretchr/testify v1.8.0/go.mod h1:yNjHg4UonilssWZ8iaSj1OCr/vHnekPRkoO+kdMU+MU=
+github.com/stretchr/testify v1.8.4 h1:CcVxjf3Q8PM0mHUKJCdn+eZZtm5yQwehR5yeSVQQcUk=
+github.com/stretchr/testify v1.8.4/go.mod h1:sz/lmYIOXD/1dqDmKjjqLyZ2RngseejIcXlSw2iwfAo=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 h1:epCh84lMvA70Z7CTTCmYQn2CKbY8j86K7/FAIr141uY=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7/go.mod h1:q4W45IWZaF22tdD+VEXcAWRA037jwmWEB5VWYORlTpc=
 golang.org/x/crypto v0.0.0-20170930174604-9419663f5a44/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
@@ -107,5 +114,6 @@ gopkg.in/tomb.v1 v1.0.0-20141024135613-dd632973f1e7/go.mod h1:dt/ZhP58zS4L8KSrWD
 gopkg.in/yaml.v2 v2.2.1/go.mod h1:hI93XBmqTisBFMUTm0b8Fm+jr3Dg1NNxqwp+5A1VGuI=
 gopkg.in/yaml.v2 v2.2.4/go.mod h1:hI93XBmqTisBFMUTm0b8Fm+jr3Dg1NNxqwp+5A1VGuI=
 gopkg.in/yaml.v2 v2.3.0/go.mod h1:hI93XBmqTisBFMUTm0b8Fm+jr3Dg1NNxqwp+5A1VGuI=
-gopkg.in/yaml.v3 v3.0.0-20200313102051-9f266ea9e77c h1:dUUwHk2QECo/6vqA44rthZ8ie2QXMNeKRTHCNY2nXvo=
 gopkg.in/yaml.v3 v3.0.0-20200313102051-9f266ea9e77c/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
+gopkg.in/yaml.v3 v3.0.1 h1:fxVm/GzAzEWqLHuvctI91KS9hhNmmWOoWu0XTYJS7CA=
+gopkg.in/yaml.v3 v3.0.1/go.mod h1:K4uyk7z7BCEPqu6E+C64Yfv1cQ7kz7rIZviUmN+EgEM=
```
