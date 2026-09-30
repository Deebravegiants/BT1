# [?] fix(bridge-history+rollup-relayer): update da-codec to prevent zstd deadlock (#1724)

## Summary
Severity: Unknown
Chain: Scroll
Component: scroll-tech/scroll
Published: 2025-08-25
Source: https://github.com/scroll-tech/scroll/commit/1552e98b798a7755a60930b9e1d539aa6abc81f1
Type: security-commit

## Details
fix(bridge-history+rollup-relayer): update da-codec to prevent zstd deadlock (#1724)

Co-authored-by: yiweichi <yiweichi@users.noreply.github.com>
Co-authored-by: Péter Garamvölgyi <peter@scroll.io>

## Patch
### bridge-history-api/go.mod
```diff
@@ -10,7 +10,7 @@ require (
 	github.com/go-redis/redis/v8 v8.11.5
 	github.com/pressly/goose/v3 v3.16.0
 	github.com/prometheus/client_golang v1.19.0
-	github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6
+	github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6
 	github.com/scroll-tech/go-ethereum v1.10.14-0.20250729113104-bd8f141bb3e9
 	github.com/stretchr/testify v1.9.0
 	github.com/urfave/cli/v2 v2.25.7
```

### bridge-history-api/go.sum
```diff
@@ -309,8 +309,8 @@ github.com/rs/cors v1.7.0 h1:+88SsELBHx5r+hZ8TCkggzSstaWNbDvThkVK8H6f9ik=
 github.com/rs/cors v1.7.0/go.mod h1:gFx+x8UowdsKA9AchylcLynDq+nNFfI8FkUZdN/jGCU=
 github.com/russross/blackfriday/v2 v2.1.0 h1:JIOH55/0cWyOuilr9/qlrm0BSXldqnqwMsf35Ld67mk=
 github.com/russross/blackfriday/v2 v2.1.0/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6 h1:vb2XLvQwCf+F/ifP6P/lfeiQrHY6+Yb/E3R4KHXLqSE=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6 h1:EiLZgoRfGgF0QzZ1jGSlo60A6W7g9L/8XLWMhwwtKJ0=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250729113104-bd8f141bb3e9 h1:u371VK8eOU2Z/0SVf5KDI3eJc8msHSpJbav4do/8n38=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250729113104-bd8f141bb3e9/go.mod h1:pDCZ4iGvEGmdIe4aSAGBrb7XSrKEML6/L/wEMmNxOdk=
 github.com/scroll-tech/zktrie v0.8.4 h1:UagmnZ4Z3ITCk+aUq9NQZJNAwnWl4gSxsLb2Nl7IgRE=
```

### common/go.mod
```diff
@@ -15,7 +15,7 @@ require (
 	github.com/modern-go/reflect2 v1.0.2
 	github.com/orcaman/concurrent-map v1.0.0
 	github.com/prometheus/client_golang v1.19.0
-	github.com/scroll-tech/go-ethereum v1.10.14-0.20250305151038-478940e79601
+	github.com/scroll-tech/go-ethereum v1.10.14-0.20250625112225-a67863c65587
 	github.com/stretchr/testify v1.10.0
 	github.com/testcontainers/testcontainers-go v0.30.0
 	github.com/testcontainers/testcontainers-go/modules/compose v0.30.0
@@ -184,7 +184,7 @@ require (
 	github.com/rjeczalik/notify v0.9.1 // indirect
 	github.com/rs/cors v1.7.0 // indirect
 	github.com/russross/blackfriday/v2 v2.1.0 // indirect
-	github.com/scroll-tech/da-codec v0.1.3-0.20250310095435-012aaee6b435 // indirect
+	github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6 // indirect
 	github.com/scroll-tech/zktrie v0.8.4 // indirect
 	github.com/secure-systems-lab/go-securesystemslib v0.4.0 // indirect
 	github.com/serialx/hashring v0.0.0-20190422032157-8b2912629002 // indirect
```

### common/go.sum
```diff
@@ -636,10 +636,10 @@ github.com/rs/cors v1.7.0 h1:+88SsELBHx5r+hZ8TCkggzSstaWNbDvThkVK8H6f9ik=
 github.com/rs/cors v1.7.0/go.mod h1:gFx+x8UowdsKA9AchylcLynDq+nNFfI8FkUZdN/jGCU=
 github.com/russross/blackfriday/v2 v2.1.0 h1:JIOH55/0cWyOuilr9/qlrm0BSXldqnqwMsf35Ld67mk=
 github.com/russross/blackfriday/v2 v2.1.0/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
-github.com/scroll-tech/da-codec v0.1.3-0.20250310095435-012aaee6b435 h1:X9fkvjrYBY79lGgKEPpUhuiJ4vWpWwzOVw4H8CU8L54=
-github.com/scroll-tech/da-codec v0.1.3-0.20250310095435-012aaee6b435/go.mod h1:yhTS9OVC0xQGhg7DN5iV5KZJvnSIlFWAxDdp+6jxQtY=
-github.com/scroll-tech/go-ethereum v1.10.14-0.20250305151038-478940e79601 h1:NEsjCG6uSvLRBlsP3+x6PL1kM+Ojs3g8UGotIPgJSz8=
-github.com/scroll-tech/go-ethereum v1.10.14-0.20250305151038-478940e79601/go.mod h1:OblWe1+QrZwdpwO0j/LY3BSGuKT3YPUFBDQQgvvfStQ=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6 h1:EiLZgoRfGgF0QzZ1jGSlo60A6W7g9L/8XLWMhwwtKJ0=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
+github.com/scroll-tech/go-ethereum v1.10.14-0.20250625112225-a67863c65587 h1:wG1+gb+K4iLtxAHhiAreMdIjP5x9hB64duraN2+u1QU=
+github.com/scroll-tech/go-ethereum v1.10.14-0.20250625112225-a67863c65587/go.mod h1:YyfB2AyAtphlbIuDQgaxc2b9mo0zE4EBA1+qtXvzlmg=
 github.com/scroll-tech/zktrie v0.8.4 h1:UagmnZ4Z3ITCk+aUq9NQZJNAwnWl4gSxsLb2Nl7IgRE=
 github.com/scroll-tech/zktrie v0.8.4/go.mod h1:XvNo7vAk8yxNyTjBDj5WIiFzYW4bx/gJ78+NK6Zn6Uk=
 github.com/secure-systems-lab/go-securesystemslib v0.4.0 h1:b23VGrQhTA8cN2CbBw7/FulN9fTtqYUdS5+Oxzt+DUE=
```

### common/version/version.go
```diff
@@ -5,7 +5,7 @@ import (
 	"runtime/debug"
 )
 
-var tag = "v4.5.41"
+var tag = "v4.5.42"
 
 var commit = func() string {
 	if info, ok := debug.ReadBuildInfo(); ok {
```

### coordinator/go.mod
```diff
@@ -9,7 +9,7 @@ require (
 	github.com/google/uuid v1.6.0
 	github.com/mitchellh/mapstructure v1.5.0
 	github.com/prometheus/client_golang v1.19.0
-	github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6
+	github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6
 	github.com/scroll-tech/go-ethereum v1.10.14-0.20250626110859-cc9a1dd82de7
 	github.com/shopspring/decimal v1.3.1
 	github.com/stretchr/testify v1.10.0
```

### coordinator/go.sum
```diff
@@ -253,8 +253,8 @@ github.com/rs/cors v1.7.0 h1:+88SsELBHx5r+hZ8TCkggzSstaWNbDvThkVK8H6f9ik=
 github.com/rs/cors v1.7.0/go.mod h1:gFx+x8UowdsKA9AchylcLynDq+nNFfI8FkUZdN/jGCU=
 github.com/russross/blackfriday/v2 v2.1.0 h1:JIOH55/0cWyOuilr9/qlrm0BSXldqnqwMsf35Ld67mk=
 github.com/russross/blackfriday/v2 v2.1.0/go.mod h1:+Rmxgy9KzJVeS9/2gXHxylqXiyQDYRxCVz55jmeOWTM=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6 h1:vb2XLvQwCf+F/ifP6P/lfeiQrHY6+Yb/E3R4KHXLqSE=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6 h1:EiLZgoRfGgF0QzZ1jGSlo60A6W7g9L/8XLWMhwwtKJ0=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250626110859-cc9a1dd82de7 h1:1rN1qocsQlOyk1VCpIEF1J5pfQbLAi1pnMZSLQS37jQ=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250626110859-cc9a1dd82de7/go.mod h1:pDCZ4iGvEGmdIe4aSAGBrb7XSrKEML6/L/wEMmNxOdk=
 github.com/scroll-tech/zktrie v0.8.4 h1:UagmnZ4Z3ITCk+aUq9NQZJNAwnWl4gSxsLb2Nl7IgRE=
```

### go.work.sum
```diff
@@ -1408,13 +1408,12 @@ github.com/scroll-tech/da-codec v0.1.3-0.20250609113414-f33adf0904bd h1:NUol+dPt
 github.com/scroll-tech/da-codec v0.1.3-0.20250609113414-f33adf0904bd/go.mod h1:gz5x3CsLy5htNTbv4PWRPBU9nSAujfx1U2XtFcXoFuk=
 github.com/scroll-tech/da-codec v0.1.3-0.20250609154559-8935de62c148 h1:cyK1ifU2fRoMl8YWR9LOsZK4RvJnlG3RODgakj5I8VY=
 github.com/scroll-tech/da-codec v0.1.3-0.20250609154559-8935de62c148/go.mod h1:gz5x3CsLy5htNTbv4PWRPBU9nSAujfx1U2XtFcXoFuk=
+github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20240607130425-e2becce6a1a4/go.mod h1:byf/mZ8jLYUCnUePTicjJWn+RvKdxDn7buS6glTnMwQ=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20240821074444-b3fa00861e5e/go.mod h1:swB5NSp8pKNDuYsTxfR08bHS6L56i119PBx8fxvV8Cs=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20241010064814-3d88e870ae22/go.mod h1:r9FwtxCtybMkTbWYCyBuevT9TW3zHmOTHqD082Uh+Oo=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250206083728-ea43834c198f/go.mod h1:Ik3OBLl7cJxPC+CFyCBYNXBPek4wpdzkWehn/y5qLM8=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250225152658-bcfdb48dd939/go.mod h1:AgU8JJxC7+nfs7R7ma35AU7dMAGW7wCw3dRZRefIKyQ=
-github.com/scroll-tech/go-ethereum v1.10.14-0.20250729113104-bd8f141bb3e9 h1:u371VK8eOU2Z/0SVf5KDI3eJc8msHSpJbav4do/8n38=
-github.com/scroll-tech/go-ethereum v1.10.14-0.20250729113104-bd8f141bb3e9/go.mod h1:pDCZ4iGvEGmdIe4aSAGBrb7XSrKEML6/L/wEMmNxOdk=
 github.com/sean-/seed v0.0.0-20170313163322-e2103e2c3529 h1:nn5Wsu0esKSJiIVhscUtVbo7ada43DJhG55ua/hjS5I=
 github.com/sean-/seed v0.0.0-20170313163322-e2103e2c3529/go.mod h1:DxrIzT+xaE7yg65j358z/aeFdxmN0P9QXhEzd20vsDc=
 github.com/segmentio/kafka-go v0.1.0/go.mod h1:X6itGqS9L4jDletMsxZ7Dz+JFWxM6JHfPOCvTvk+EJo=
```

### rollup/go.mod
```diff
@@ -15,7 +15,7 @@ require (
 	github.com/holiman/uint256 v1.3.2
 	github.com/mitchellh/mapstructure v1.5.0
 	github.com/prometheus/client_golang v1.16.0
-	github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6
+	github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6
 	github.com/scroll-tech/go-ethereum v1.10.14-0.20250626110859-cc9a1dd82de7
 	github.com/smartystreets/goconvey v1.8.0
 	github.com/spf13/viper v1.19.0
```

### rollup/go.sum
```diff
@@ -285,8 +285,8 @@ github.com/sagikazarmark/locafero v0.4.0 h1:HApY1R9zGo4DBgr7dqsTH/JJxLTTsOt7u6ke
 github.com/sagikazarmark/locafero v0.4.0/go.mod h1:Pe1W6UlPYUk/+wc/6KFhbORCfqzgYEpgQ3O5fPuL3H4=
 github.com/sagikazarmark/slog-shim v0.1.0 h1:diDBnUNK9N/354PgrxMywXnAwEr1QZcOr6gto+ugjYE=
 github.com/sagikazarmark/slog-shim v0.1.0/go.mod h1:SrcSrq8aKtyuqEI1uvTDTK1arOWRIczQRv+GVI1AkeQ=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6 h1:vb2XLvQwCf+F/ifP6P/lfeiQrHY6+Yb/E3R4KHXLqSE=
-github.com/scroll-tech/da-codec v0.1.3-0.20250626091118-58b899494da6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6 h1:EiLZgoRfGgF0QzZ1jGSlo60A6W7g9L/8XLWMhwwtKJ0=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250626110859-cc9a1dd82de7 h1:1rN1qocsQlOyk1VCpIEF1J5pfQbLAi1pnMZSLQS37jQ=
 github.com/scroll-tech/go-ethereum v1.10.14-0.20250626110859-cc9a1dd82de7/go.mod h1:pDCZ4iGvEGmdIe4aSAGBrb7XSrKEML6/L/wEMmNxOdk=
 github.com/scroll-tech/zktrie v0.8.4 h1:UagmnZ4Z3ITCk+aUq9NQZJNAwnWl4gSxsLb2Nl7IgRE=
```

### tests/integration-test/go.mod
```diff
@@ -5,8 +5,8 @@ go 1.22
 toolchain go1.22.2
 
 require (
-	github.com/scroll-tech/da-codec v0.1.3-0.20250310095435-012aaee6b435
-	github.com/scroll-tech/go-ethereum v1.10.14-0.20250305151038-478940e79601
+	github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6
+	github.com/scroll-tech/go-ethereum v1.10.14-0.20250625112225-a67863c65587
 	github.com/stretchr/testify v1.10.0
 	gorm.io/gorm v1.25.7-0.20240204074919-46816ad31dde
 )
```

### tests/integration-test/go.sum
```diff
@@ -93,10 +93,10 @@ github.com/rjeczalik/notify v0.9.1 h1:CLCKso/QK1snAlnhNR/CNvNiFU2saUtjV0bx3EwNeC
 github.com/rjeczalik/notify v0.9.1/go.mod h1:rKwnCoCGeuQnwBtTSPL9Dad03Vh2n40ePRrjvIXnJho=
 github.com/rogpeppe/go-internal v1.12.0 h1:exVL4IDcn6na9z1rAb56Vxr+CgyK3nn3O+epU5NdKM8=
 github.com/rogpeppe/go-internal v1.12.0/go.mod h1:E+RYuTGaKKdloAfM02xzb0FW3Paa99yedzYV+kq4uf4=
-github.com/scroll-tech/da-codec v0.1.3-0.20250310095435-012aaee6b435 h1:X9fkvjrYBY79lGgKEPpUhuiJ4vWpWwzOVw4H8CU8L54=
-github.com/scroll-tech/da-codec v0.1.3-0.20250310095435-012aaee6b435/go.mod h1:yhTS9OVC0xQGhg7DN5iV5KZJvnSIlFWAxDdp+6jxQtY=
-github.com/scroll-tech/go-ethereum v1.10.14-0.20250305151038-478940e79601 h1:NEsjCG6uSvLRBlsP3+x6PL1kM+Ojs3g8UGotIPgJSz8=
-github.com/scroll-tech/go-ethereum v1.10.14-0.20250305151038-478940e79601/go.mod h1:OblWe1+QrZwdpwO0j/LY3BSGuKT3YPUFBDQQgvvfStQ=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6 h1:EiLZgoRfGgF0QzZ1jGSlo60A6W7g9L/8XLWMhwwtKJ0=
+github.com/scroll-tech/da-codec v0.1.3-0.20250825071838-cddc263e5ef6/go.mod h1:Z6kN5u2khPhiqHyk172kGB7o38bH/nj7Ilrb/46wZGg=
+github.com/scroll-tech/go-ethereum v1.10.14-0.20250625112225-a67863c65587 h1:wG1+gb+K4iLtxAHhiAreMdIjP5x9hB64duraN2+u1QU=
+github.com/scroll-tech/go-ethereum v1.10.14-0.20250625112225-a67863c65587/go.mod h1:YyfB2AyAtphlbIuDQgaxc2b9mo0zE4EBA1+qtXvzlmg=
 github.com/scroll-tech/zktrie v0.8.4 h1:UagmnZ4Z3ITCk+aUq9NQZJNAwnWl4gSxsLb2Nl7IgRE=
 github.com/scroll-tech/zktrie v0.8.4/go.mod h1:XvNo7vAk8yxNyTjBDj5WIiFzYW4bx/gJ78+NK6Zn6Uk=
 github.com/shirou/gopsutil v3.21.11+incompatible h1:+1+c1VGhc88SSonWP6foOcLhvnKlUeu/erjjvaPEYiI=
```
