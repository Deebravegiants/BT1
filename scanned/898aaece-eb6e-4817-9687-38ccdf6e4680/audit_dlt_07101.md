# [?] Update jwt-go library to fix CVE-2020-26160 (#9017)

## Summary
Severity: Unknown
Chain: Ethereum
Component: prysmaticlabs/prysm
Published: 2021-06-10
Source: https://github.com/OffchainLabs/prysm/commit/8f90e91e993dc71dd6c014b107ad05726dbcb95f
Type: security-commit

## Details
Update jwt-go library to fix CVE-2020-26160 (#9017)

* Replace github.com/dgrijalva/jwt-go with github.com/form3tech-oss/jwt-go, including security fix

* Fix to include go cast in deps.bzl and go mod

* Add gocast stub for go.mod / deps.bzl trick

* revert some changes

* Remove ignore tag

* gaz

* go mod tidy

* add build exclusion

* Go mod?

* go mod tidy

## Patch
### deps.bzl
```diff
@@ -839,6 +839,13 @@ def prysm_deps():
         sum = "h1:WXb3TSNmHp2vHoCroCIB1foO/yQ36swABL8aOVeDpgg=",
         version = "v1.2.1-0.20190220221249-0403632d5b90",
     )
+    go_repository(
+        name = "com_github_form3tech_oss_jwt_go",
+        importpath = "github.com/form3tech-oss/jwt-go",
+        sum = "h1:xdtqez379uWVJ9P3qQMX8W+F/nqsTdUvyMZB36tnacA=",
+        version = "v3.2.1+incompatible",
+    )
+
     go_repository(
         name = "com_github_fortytw2_leaktest",
         importpath = "github.com/fortytw2/leaktest",
@@ -1786,6 +1793,12 @@ def prysm_deps():
         version = "v1.2.3",
     )
 
+    go_repository(
+        name = "com_github_klauspost_cpuid_v2",
+        importpath = "github.com/klauspost/cpuid/v2",
+        sum = "h1:g0I61F2K2DjRHz1cnxlkNSBIaePVoJIjjnHui8QHbiw=",
+        version = "v2.0.4",
+    )
     go_repository(
         name = "com_github_klauspost_crc32",
         importpath = "github.com/klauspost/crc32",
@@ -3858,9 +3871,3 @@ def prysm_deps():
         sum = "h1:uFRZXykJGK9lLY4HtgSw44DnIcAM+kRBP7x5m+NpAOM=",
         version = "v1.16.0",
     )
-    go_repository(
-        name = "com_github_klauspost_cpuid_v2",
-        importpath = "github.com/klauspost/cpuid/v2",
-        sum = "h1:g0I61F2K2DjRHz1cnxlkNSBIaePVoJIjjnHui8QHbiw=",
-        version = "v2.0.4",
-    )
```

### go.mod
```diff
@@ -17,13 +17,13 @@ require (
 	github.com/davidlazar/go-crypto v0.0.0-20200604182044-b73af7476f6c // indirect
 	github.com/deckarep/golang-set v1.7.1 // indirect
 	github.com/dgraph-io/ristretto v0.0.4-0.20210318174700-74754f61e018
-	github.com/dgrijalva/jwt-go v3.2.0+incompatible
 	github.com/dlclark/regexp2 v1.4.0 // indirect
 	github.com/emicklei/dot v0.11.0
 	github.com/ethereum/go-ethereum v1.9.25
 	github.com/fatih/color v1.9.0 // indirect
 	github.com/ferranbt/fastssz v0.0.0-20210526181520-7df50c8568f8
 	github.com/fjl/memsize v0.0.0-20190710130421-bcb5799ab5e5
+	github.com/form3tech-oss/jwt-go v3.2.1+incompatible
 	github.com/fsnotify/fsnotify v1.4.9
 	github.com/gballet/go-libpcsclite v0.0.0-20191108122812-4678299bea08 // indirect
 	github.com/ghodss/yaml v1.0.0
@@ -89,6 +89,7 @@ require (
 	github.com/prysmaticlabs/eth2-types v0.0.0-20210303084904-c9735a06829d
 	github.com/prysmaticlabs/go-bitfield v0.0.0-20210515192923-def021850363
 	github.com/prysmaticlabs/prombbolt v0.0.0-20210126082820-9b7adba6db7c
+	github.com/prysmaticlabs/protoc-gen-go-cast v0.0.0-20210504233148-1e141af6a0a1
 	github.com/rs/cors v1.7.0
 	github.com/schollz/progressbar/v3 v3.3.4
 	github.com/sirupsen/logrus v1.6.0
```

### go.sum
```diff
@@ -276,6 +276,8 @@ github.com/fjl/memsize v0.0.0-20190710130421-bcb5799ab5e5/go.mod h1:VvhXpOYNQvB+
 github.com/flynn/noise v0.0.0-20180327030543-2492fe189ae6 h1:u/UEqS66A5ckRmS4yNpjmVH56sVtS/RfclBAYocb4as=
 github.com/flynn/noise v0.0.0-20180327030543-2492fe189ae6/go.mod h1:1i71OnUq3iUe1ma7Lr6yG6/rjvM3emb6yoL7xLFzcVQ=
 github.com/fogleman/gg v1.2.1-0.20190220221249-0403632d5b90/go.mod h1:R/bRT+9gY/C5z7JzPU0zXsXHKM4/ayA+zqcVNZzPa1k=
+github.com/form3tech-oss/jwt-go v3.2.1+incompatible h1:xdtqez379uWVJ9P3qQMX8W+F/nqsTdUvyMZB36tnacA=
+github.com/form3tech-oss/jwt-go v3.2.1+incompatible/go.mod h1:pbq4aXjuKjdthFRnoDwaVPLA+WlJuPGy+QneDUgJi2k=
 github.com/fortytw2/leaktest v1.3.0/go.mod h1:jDsjWgpAGjm2CA7WthBh/CdZYEPF31XHquHwclZch5g=
 github.com/franela/goblin v0.0.0-20200105215937-c9ffbefa60db/go.mod h1:7dvUGVsVBjqR7JHJk0brhHOZYGmfBYOrK0ZhYMEtBr4=
 github.com/franela/goreq v0.0.0-20171204163338-bcd34c9993f8/go.mod h1:ZhphrRTfi2rbfLwlschooIH4+wKKDR4Pdxhh+TRoA20=
@@ -493,6 +495,8 @@ github.com/huin/goupnp v1.0.0/go.mod h1:n9v9KO1tAxYH82qOn+UTIFQDmx5n1Zxd/ClZDMX7
 github.com/huin/goupnp v1.0.1-0.20210310174557-0ca763054c88 h1:bcAj8KroPf552TScjFPIakjH2/tdIrIH8F+cc4v4SRo=
 github.com/huin/goupnp v1.0.1-0.20210310174557-0ca763054c88/go.mod h1:nNs7wvRfN1eKaMknBydLNQU6146XQim8t4h+q90biWo=
 github.com/huin/goutil v0.0.0-20170803182201-1ca381bf3150/go.mod h1:PpLOETDnJ0o3iZrZfqZzyLl6l7F3c6L1oWn7OICBi6o=
+github.com/iancoleman/strcase v0.1.3 h1:dJBk1m2/qjL1twPLf68JND55vvivMupZ4wIzE8CTdBw=
+github.com/iancoleman/strcase v0.1.3/go.mod h1:SK73tn/9oHe+/Y0h39VT4UCxmurVJkR5NA7kMEAOgSE=
 github.com/ianlancetaylor/cgosymbolizer v0.0.0-20200424224625-be1b05b0b279 h1:IpTHAzWv1pKDDWeJDY5VOHvqc2T9d3C8cPKEf2VPqHE=
 github.com/ianlancetaylor/cgosymbolizer v0.0.0-20200424224625-be1b05b0b279/go.mod h1:a5aratAVTWyz+nJMmDsN8O4XTfaLfdAsB1ysCmZX5Bw=
 github.com/ianlancetaylor/demangle v0.0.0-20181102032728-5e5cf60278f6/go.mod h1:aSSvb/t6k1mPoxDqO4vJh6VOCGPwU4O0C2/Eqndh1Sc=
@@ -1085,12 +1089,15 @@ github.com/prysmaticlabs/bazel-go-ethereum v0.0.0-20210420143944-f4dfc9744288 h1
 github.com/prysmaticlabs/bazel-go-ethereum v0.0.0-20210420143944-f4dfc9744288/go.mod h1:YmSRTZNqAvVUg3BIG8uhT/BOkFk9+R2iCbxw5zOlnWY=
 github.com/prysmaticlabs/eth2-types v0.0.0-20210303084904-c9735a06829d h1:1dN7YAqMN3oAJ0LceWcyv/U4jHLh+5urnSnr4br6zg4=
 github.com/prysmaticlabs/eth2-types v0.0.0-20210303084904-c9735a06829d/go.mod h1:kOmQ/zdobQf7HUohDTifDNFEZfNaSCIY5fkONPL+dWU=
+github.com/prysmaticlabs/go-bitfield v0.0.0-20210108222456-8e92c3709aa0/go.mod h1:hCwmef+4qXWjv0jLDbQdWnL0Ol7cS7/lCSS26WR+u6s=
 github.com/prysmaticlabs/go-bitfield v0.0.0-20210515192923-def021850363 h1:n1fCZPIMlcNQ3iCN5w4vxmFFNWhEdEz3ICTerxjUFvA=
 github.com/prysmaticlabs/go-bitfield v0.0.0-20210515192923-def021850363/go.mod h1:hCwmef+4qXWjv0jLDbQdWnL0Ol7cS7/lCSS26WR+u6s=
 github.com/prysmaticlabs/grpc-gateway/v2 v2.3.1-0.20210604200058-f148bcf3f503 h1:QzTDCXA7FV2tIJ7TGHfEsYfa8QaAeMB1F4B5jAsGQNg=
 github.com/prysmaticlabs/grpc-gateway/v2 v2.3.1-0.20210604200058-f148bcf3f503/go.mod h1:IOyTYjcIO0rkmnGBfJTL0NJ11exy/Tc2QEuv7hCXp24=
 github.com/prysmaticlabs/prombbolt v0.0.0-20210126082820-9b7adba6db7c h1:9PHRCuO/VN0s9k+RmLykho7AjDxblNYI5bYKed16NPU=
 github.com/prysmaticlabs/prombbolt v0.0.0-20210126082820-9b7adba6db7c/go.mod h1:ZRws458tYHS/Zs936OQ6oCrL+Ict5O4Xpwve1UQ6C9M=
+github.com/prysmaticlabs/protoc-gen-go-cast v0.0.0-20210504233148-1e141af6a0a1 h1:k7CCMwN7VooQ7GhfySnaVyI4/9+QbhJTdasoC6VOZOI=
+github.com/prysmaticlabs/protoc-gen-go-cast v0.0.0-20210504233148-1e141af6a0a1/go.mod h1:au9l1XcWNEKixIlSRzEe54fYGhyELWgJJIxKu8W75Mc=
 github.com/rcrowley/go-metrics v0.0.0-20181016184325-3113b8401b8a/go.mod h1:bCqnVzQkZxMG4s8nGwiZ5l3QUCyqpo9Y+/ZMZ9VjZe4=
 github.com/rcrowley/go-metrics v0.0.0-20190826022208-cac0b30c2563/go.mod h1:bCqnVzQkZxMG4s8nGwiZ5l3QUCyqpo9Y+/ZMZ9VjZe4=
 github.com/retailnext/hllpp v1.0.1-0.20180308014038-101a6d2f8b52/go.mod h1:RDpi1RftBQPUCDRw6SmxeaREsAaRKnOclghuzp/WRzc=
```

### proto/testing/gocast.go
```diff
@@ -0,0 +1,8 @@
+// +build tools
+
+package testing
+
+// Trick go mod into requiring protoc-gen-go-cast and therefore Gazelle won't prune it.
+import (
+	_ "github.com/prysmaticlabs/protoc-gen-go-cast"
+)
```

### validator/rpc/BUILD.bazel
```diff
@@ -43,7 +43,7 @@ go_library(
         "//validator/keymanager/derived:go_default_library",
         "//validator/keymanager/imported:go_default_library",
         "//validator/slashing-protection/local/standard-protection-format:go_default_library",
-        "@com_github_dgrijalva_jwt_go//:go_default_library",
+        "@com_github_form3tech_oss_jwt_go//:go_default_library",
         "@com_github_grpc_ecosystem_go_grpc_middleware//:go_default_library",
         "@com_github_grpc_ecosystem_go_grpc_middleware//recovery:go_default_library",
         "@com_github_grpc_ecosystem_go_grpc_middleware//retry:go_default_library",
@@ -103,7 +103,7 @@ go_test(
         "//validator/keymanager/imported:go_default_library",
         "//validator/slashing-protection/local/standard-protection-format/format:go_default_library",
         "//validator/testing:go_default_library",
-        "@com_github_dgrijalva_jwt_go//:go_default_library",
+        "@com_github_form3tech_oss_jwt_go//:go_default_library",
         "@com_github_golang_mock//gomock:go_default_library",
         "@com_github_google_uuid//:go_default_library",
         "@com_github_pkg_errors//:go_default_library",
```

### validator/rpc/auth.go
```diff
@@ -5,7 +5,7 @@ import (
 	"path/filepath"
 	"time"
 
-	"github.com/dgrijalva/jwt-go"
+	"github.com/form3tech-oss/jwt-go"
 	"github.com/golang/protobuf/ptypes/empty"
 	"github.com/pkg/errors"
 	pb "github.com/prysmaticlabs/prysm/proto/validator/accounts/v2"
```

### validator/rpc/auth_test.go
```diff
@@ -6,7 +6,7 @@ import (
 	"path/filepath"
 	"testing"
 
-	"github.com/dgrijalva/jwt-go"
+	"github.com/form3tech-oss/jwt-go"
 	"github.com/golang/protobuf/ptypes/empty"
 	pb "github.com/prysmaticlabs/prysm/proto/validator/accounts/v2"
 	"github.com/prysmaticlabs/prysm/shared/event"
```

### validator/rpc/intercepter.go
```diff
@@ -6,7 +6,7 @@ import (
 	"strings"
 	"sync"
 
-	"github.com/dgrijalva/jwt-go"
+	"github.com/form3tech-oss/jwt-go"
 	"google.golang.org/grpc"
 	"google.golang.org/grpc/codes"
 	"google.golang.org/grpc/metadata"
```

### validator/rpc/intercepter_test.go
```diff
@@ -4,7 +4,7 @@ import (
 	"context"
 	"testing"
 
-	"github.com/dgrijalva/jwt-go"
+	"github.com/form3tech-oss/jwt-go"
 	"github.com/prysmaticlabs/prysm/shared/testutil/require"
 	"github.com/prysmaticlabs/prysm/shared/timeutils"
 	"google.golang.org/grpc"
```
