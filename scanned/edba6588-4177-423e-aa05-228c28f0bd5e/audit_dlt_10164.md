# [?] Merge pull request #6556 from oasisprotocol/martin/fix-go-vulnerabilities

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2026-08-04
Source: https://github.com/oasisprotocol/oasis-core/commit/27cd0fcf08130dd9ea1cdb80be53cb25b09132b7
Type: security-commit

## Details
Merge pull request #6556 from oasisprotocol/martin/fix-go-vulnerabilities

Update vulnerable go dependencies

## Patch
### .changelog/6556.internal.1.md
```diff
@@ -0,0 +1 @@
+go: Bump golang.org/x/net to v0.57.0
```

### .changelog/6556.internal.2.md
```diff
@@ -0,0 +1 @@
+go: Bump github.com/klauspost/compress to v1.18.7
```

### .changelog/6556.internal.3.md
```diff
@@ -0,0 +1 @@
+go: Bump github.com/pion/stun/v3 to v3.1.6
```

### .changelog/6556.internal.4.md
```diff
@@ -0,0 +1 @@
+go: Bump github.com/quic-go/webtransport-go to v0.11.1
```

### go/go.mod
```diff
@@ -58,8 +58,8 @@ require (
 	github.com/tyler-smith/go-bip39 v1.1.0
 	go.uber.org/zap v1.27.0
 	golang.org/x/exp v0.0.0-20250606033433-dcc06ee1d476
-	golang.org/x/net v0.55.0
-	golang.org/x/sync v0.20.0
+	golang.org/x/net v0.57.0
+	golang.org/x/sync v0.22.0
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20251202230838-ff82c1b0f217
 	google.golang.org/grpc v1.79.3
 	google.golang.org/grpc/security/advancedtls v0.0.0-20221004221323-12db695f1648
@@ -115,7 +115,7 @@ require (
 	github.com/jbenet/go-temp-err-catcher v0.1.0 // indirect
 	github.com/jmhodges/levigo v1.0.0 // indirect
 	github.com/json-iterator/go v1.1.12 // indirect
-	github.com/klauspost/compress v1.18.0 // indirect
+	github.com/klauspost/compress v1.18.7 // indirect
 	github.com/klauspost/cpuid/v2 v2.2.10 // indirect
 	github.com/koron/go-ssdp v0.0.6 // indirect
 	github.com/kr/pretty v0.3.1 // indirect
@@ -174,7 +174,7 @@ require (
 	github.com/pion/sctp v1.8.39 // indirect
 	github.com/pion/sdp/v3 v3.0.18 // indirect
 	github.com/pion/srtp/v3 v3.0.6 // indirect
-	github.com/pion/stun/v3 v3.1.1 // indirect
+	github.com/pion/stun/v3 v3.1.6 // indirect
 	github.com/pion/transport/v3 v3.0.7 // indirect
 	github.com/pion/transport/v4 v4.0.2 // indirect
 	github.com/pion/turn/v4 v4.0.2 // indirect
@@ -183,8 +183,8 @@ require (
 	github.com/pmezard/go-difflib v1.0.1-0.20181226105442-5d4384ee4fb2 // indirect
 	github.com/prometheus/client_model v0.6.2 // indirect
 	github.com/quic-go/qpack v0.6.0 // indirect
-	github.com/quic-go/quic-go v0.59.1 // indirect
-	github.com/quic-go/webtransport-go v0.10.0 // indirect
+	github.com/quic-go/quic-go v0.60.0 // indirect
+	github.com/quic-go/webtransport-go v0.11.1 // indirect
 	github.com/rcrowley/go-metrics v0.0.0-20201227073835-cf1acfcdf475 // indirect
 	github.com/rogpeppe/go-internal v1.13.1 // indirect
 	github.com/rs/cors v1.11.1 // indirect
@@ -205,13 +205,13 @@ require (
 	go.uber.org/fx v1.24.0 // indirect
 	go.uber.org/mock v0.5.2 // indirect
 	go.uber.org/multierr v1.11.0 // indirect
-	golang.org/x/crypto v0.52.0 // indirect
-	golang.org/x/mod v0.35.0 // indirect
-	golang.org/x/sys v0.45.0 // indirect
-	golang.org/x/telemetry v0.0.0-20260409153401-be6f6cb8b1fa // indirect
-	golang.org/x/text v0.37.0 // indirect
+	golang.org/x/crypto v0.54.0 // indirect
+	golang.org/x/mod v0.37.0 // indirect
+	golang.org/x/sys v0.47.0 // indirect
+	golang.org/x/telemetry v0.0.0-20260625142307-59b4966ccb57 // indirect
+	golang.org/x/text v0.40.0 // indirect
 	golang.org/x/time v0.14.0 // indirect
-	golang.org/x/tools v0.44.0 // indirect
+	golang.org/x/tools v0.47.0 // indirect
 	gopkg.in/fsnotify.v1 v1.4.7 // indirect
 	gopkg.in/ini.v1 v1.67.0 // indirect
 	gopkg.in/tomb.v1 v1.0.0-20141024135613-dd632973f1e7 // indirect
```

### go/go.sum
```diff
@@ -309,8 +309,8 @@ github.com/jstemmer/go-junit-report v0.9.1/go.mod h1:Brl9GWCQeLvo8nXZwPNNblvFj/X
 github.com/kisielk/errcheck v1.5.0/go.mod h1:pFxgyoBC7bSaBwPgfKdkLd5X25qrDl4LWUI2bnpBCr8=
 github.com/kisielk/gotool v1.0.0/go.mod h1:XhKaO+MFFWcvkIS/tQcRk01m1F5IRFswLeQ+oQHNcck=
 github.com/kkdai/bstream v0.0.0-20161212061736-f391b8402d23/go.mod h1:J+Gs4SYgM6CZQHDETBtE9HaSEkGmuNXF86RwHhHUvq4=
-github.com/klauspost/compress v1.18.0 h1:c/Cqfb0r+Yi+JtIEq73FWXVkRonBlf0CRNYc8Zttxdo=
-github.com/klauspost/compress v1.18.0/go.mod h1:2Pp+KzxcywXVXMr50+X0Q/Lsb43OQHYWRCY2AiWywWQ=
+github.com/klauspost/compress v1.18.7 h1:aUyZsS4kH3QTKurYhAOwAHxllVPnOthb3vPfnF1Ehjw=
+github.com/klauspost/compress v1.18.7/go.mod h1:cwPg85FWrGar70rWktvGQj8/hthj3wpl0PGDogxkrSQ=
 github.com/klauspost/cpuid/v2 v2.2.10 h1:tBs3QSyvjDyFTq3uoc/9xFpCuOsJQFNPiAhYdw2skhE=
 github.com/klauspost/cpuid/v2 v2.2.10/go.mod h1:hqwkgyIinND0mEev00jJYCxPNVRVXFQeu1XKlok6oO0=
 github.com/koron/go-ssdp v0.0.6 h1:Jb0h04599eq/CY7rB5YEqPS83HmRfHP2azkxMN2rFtU=
@@ -493,8 +493,8 @@ github.com/pion/sdp/v3 v3.0.18 h1:l0bAXazKHpepazVdp+tPYnrsy9dfh7ZbT8DxesH5ZnI=
 github.com/pion/sdp/v3 v3.0.18/go.mod h1:ZREGo6A9ZygQ9XkqAj5xYCQtQpif0i6Pa81HOiAdqQ8=
 github.com/pion/srtp/v3 v3.0.6 h1:E2gyj1f5X10sB/qILUGIkL4C2CqK269Xq167PbGCc/4=
 github.com/pion/srtp/v3 v3.0.6/go.mod h1:BxvziG3v/armJHAaJ87euvkhHqWe9I7iiOy50K2QkhY=
-github.com/pion/stun/v3 v3.1.1 h1:CkQxveJ4xGQjulGSROXbXq94TAWu8gIX2dT+ePhUkqw=
-github.com/pion/stun/v3 v3.1.1/go.mod h1:qC1DfmcCTQjl9PBaMa5wSn3x9IPmKxSdcCsxBcDBndM=
+github.com/pion/stun/v3 v3.1.6 h1:WnhsD0eHCiwCfKNkVx0VJJwr2Y3eV4Ueih3KJ+dfZy8=
+github.com/pion/stun/v3 v3.1.6/go.mod h1:zRUghXSQU32Lx5orJsz3uYMkIihweXb3mu5gIns02fs=
 github.com/pion/transport/v3 v3.0.7 h1:iRbMH05BzSNwhILHoBoAPxoB9xQgOaJk+591KC9P1o0=
 github.com/pion/transport/v3 v3.0.7/go.mod h1:YleKiTZ4vqNxVwh77Z0zytYi7rXHl7j6uPLGhhz9rwo=
 github.com/pion/transport/v4 v4.0.2 h1:ifYlPqNwsy6aKQ9y8yzxXlHae5431ZrH2avkD/Rn6Tk=
@@ -520,12 +520,14 @@ github.com/prometheus/common v0.64.0 h1:pdZeA+g617P7oGv1CzdTzyeShxAGrTBsolKNOLQP
 github.com/prometheus/common v0.64.0/go.mod h1:0gZns+BLRQ3V6NdaerOhMbwwRbNh9hkGINtQAsP5GS8=
 github.com/prometheus/procfs v0.16.1 h1:hZ15bTNuirocR6u0JZ6BAHHmwS1p8B4P6MRqxtzMyRg=
 github.com/prometheus/procfs v0.16.1/go.mod h1:teAbpZRB1iIAJYREa1LsoWUXykVXA1KlTmWl8x/U+Is=
+github.com/quic-go/go-ossfuzz-seeds v0.1.0 h1:APacT+iIaNF6fd8AGEiN3bT/Jtkd2jz4v4TzM7MFjy0=
+github.com/quic-go/go-ossfuzz-seeds v0.1.0/go.mod h1:3IOHRbJIc+L6YKMwfDtJAM9Vj9k0YY4muhuyUYk5tbk=
 github.com/quic-go/qpack v0.6.0 h1:g7W+BMYynC1LbYLSqRt8PBg5Tgwxn214ZZR34VIOjz8=
 github.com/quic-go/qpack v0.6.0/go.mod h1:lUpLKChi8njB4ty2bFLX2x4gzDqXwUpaO1DP9qMDZII=
-github.com/quic-go/quic-go v0.59.1 h1:0Gmua0HW1Tv7ANR7hUYwRyD0MG5OJfgvYSZasGZzBic=
-github.com/quic-go/quic-go v0.59.1/go.mod h1:upnsH4Ju1YkqpLXC305eW3yDZ4NfnNbmQRCMWS58IKU=
-github.com/quic-go/webtransport-go v0.10.0 h1:LqXXPOXuETY5Xe8ITdGisBzTYmUOy5eSj+9n4hLTjHI=
-github.com/quic-go/webtransport-go v0.10.0/go.mod h1:LeGIXr5BQKE3UsynwVBeQrU1TPrbh73MGoC6jd+V7ow=
+github.com/quic-go/quic-go v0.60.0 h1:xcQioE8OM66UQLeUMHltK1CCcOu3JbVB4JAQdDQSB+0=
+github.com/quic-go/quic-go v0.60.0/go.mod h1:wpKpjmPpftl30sL6pFh7REVpjbcCVy4zt2vDyK1TuJk=
+github.com/quic-go/webtransport-go v0.11.1 h1:rrFQMO+7/52ZDJ04fsrjIaWqn6q1z1MYo9iVFq6JtbA=
+github.com/quic-go/webtransport-go v0.11.1/go.mod h1:SHgEzUFVyj+9WUSuGB1P6Zd351Pww2leWV3SwlTovkA=
 github.com/rcrowley/go-metrics v0.0.0-20201227073835-cf1acfcdf475 h1:N/ElC8H3+5XpJzTSTfLsJV/mx9Q9g7kxmchpfZyxgzM=
 github.com/rcrowley/go-metrics v0.0.0-20201227073835-cf1acfcdf475/go.mod h1:bCqnVzQkZxMG4s8nGwiZ5l3QUCyqpo9Y+/ZMZ9VjZe4=
 github.com/rogpeppe/go-internal v1.3.0/go.mod h1:M8bDsm7K2OlrFYOpmOWEs/qY81heoFRclV5y23lUDJ4=
@@ -637,8 +639,8 @@ golang.org/x/crypto v0.0.0-20200115085410-6d4e4cb37c7d/go.mod h1:LzIPMQfyMNhhGPh
 golang.org/x/crypto v0.0.0-20200602180216-279210d13fed/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
-golang.org/x/crypto v0.52.0 h1:RMs7fP2rXdep0CftQlK8Uf+kibLm7qkCcradZWYz988=
-golang.org/x/crypto v0.52.0/go.mod h1:1QgfPxDqh0T2M/elOJtp9RvuR95kVjir0e6/BvEmGbc=
+golang.org/x/crypto v0.54.0 h1:YLIA59K4fiNzHzjnZt2tUJQjQtUWfWbeHBqKtk3eScw=
+golang.org/x/crypto v0.54.0/go.mod h1:KWL8ny2AZdGR2cWmzeHrp2azQPGogOv+HeQaVEXC2dk=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190306152737-a1d7652674e8/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190510132918-efd6b22b2522/go.mod h1:ZjyILWgesfNpC6sMxTJOJm9Kp84zZh5NQWvqDGG3Qr8=
@@ -671,8 +673,8 @@ golang.org/x/mod v0.1.1-0.20191105210325-c90efee705ee/go.mod h1:QqPTAvyqsEbceGzB
 golang.org/x/mod v0.1.1-0.20191107180719-034126e5016b/go.mod h1:QqPTAvyqsEbceGzBzNggFXnrqF1CaUcvgkdR5Ot7KZg=
 golang.org/x/mod v0.2.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
-golang.org/x/mod v0.35.0 h1:Ww1D637e6Pg+Zb2KrWfHQUnH2dQRLBQyAtpr/haaJeM=
-golang.org/x/mod v0.35.0/go.mod h1:+GwiRhIInF8wPm+4AoT6L0FA1QWAad3OMdTRx4tFYlU=
+golang.org/x/mod v0.37.0 h1:vF1DjpVEshcIqoEaauuHebaLk1O1forxjxBaVn884JQ=
+golang.org/x/mod v0.37.0/go.mod h1:m8S8VeM9r4dzDwjrKO0a1sZP3YjeMamRRlD+fmR2Q/0=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -705,8 +707,8 @@ golang.org/x/net v0.0.0-20201021035429-f5854403a974/go.mod h1:sp8m0HH+o8qH0wwXwY
 golang.org/x/net v0.0.0-20201110031124-69a78807bb2b/go.mod h1:sp8m0HH+o8qH0wwXwYZr8TS3Oi6o0r6Gce1SSxlDquU=
 golang.org/x/net v0.0.0-20210119194325-5f4716e94777/go.mod h1:m0MpNAwzfU5UDzcl9v0D8zg8gWTRqZa9RBIspLL5mdg=
 golang.org/x/net v0.0.0-20210226172049-e18ecbb05110/go.mod h1:m0MpNAwzfU5UDzcl9v0D8zg8gWTRqZa9RBIspLL5mdg=
-golang.org/x/net v0.55.0 h1:bcvxaJn3e1U6InsFWt1JUq1aSjnRxLzT2rtD2KfkDF8=
-golang.org/x/net v0.55.0/go.mod h1:L5U2KuzuOe1lY7Z+aWVIKK6qEeJXnXV9yzGA+WCHJww=
+golang.org/x/net v0.57.0 h1:K5+3DljvIuDG9/Jv9rvyMywYNFCQ9RSUY6OOTTkT+tE=
+golang.org/x/net v0.57.0/go.mod h1:KpXc8iv+r3XplLAG/f7Jsf9RPszJzdR0f58q9vGOuEU=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20190226205417-e64efc72b421/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
 golang.org/x/oauth2 v0.0.0-20190604053449-0f29369cfe45/go.mod h1:gOpvHmFTYa4IltrdGE7lF6nIHvwfUNPOp7c8zoXwtLw=
@@ -724,8 +726,8 @@ golang.org/x/sync v0.0.0-20200317015054-43a5402ce75a/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.20.0 h1:e0PTpb7pjO8GAtTs2dQ6jYa5BWYlMuX047Dco/pItO4=
-golang.org/x/sync v0.20.0/go.mod h1:9xrNwdLfx4jkKbNva9FpL6vEN7evnE43NNNJQ2LF3+0=
+golang.org/x/sync v0.22.0 h1:SZjpbeLmrCk4xhRSZFNZW5gFUeCeFgjekvI/+gfScek=
+golang.org/x/sync v0.22.0/go.mod h1:9xrNwdLfx4jkKbNva9FpL6vEN7evnE43NNNJQ2LF3+0=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180909124046-d0be0721c37e/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20190215142949-d0b11bdaac8a/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -769,18 +771,18 @@ golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.21.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.45.0 h1:dO4czNzziLiiXplLQgBCEpCvXQ3dnkn0SdaZSYdQ+FY=
-golang.org/x/sys v0.45.0/go.mod h1:4GL1E5IUh+htKOUEOaiffhrAeqysfVGipDYzABqnCmw=
-golang.org/x/telemetry v0.0.0-20260409153401-be6f6cb8b1fa h1:efT73AJZfAAUV7SOip6pWGkwJDzIGiKBZGVzHYa+ve4=
-golang.org/x/telemetry v0.0.0-20260409153401-be6f6cb8b1fa/go.mod h1:kHjTxDEnAu6/Nl9lDkzjWpR+bmKfxeiRuSDlsMb70gE=
+golang.org/x/sys v0.47.0 h1:o7XGOvZQCADBQQ4Y7VNq2dRWQR7JmOUW8Kxx4ZsNgWs=
+golang.org/x/sys v0.47.0/go.mod h1:4GL1E5IUh+htKOUEOaiffhrAeqysfVGipDYzABqnCmw=
+golang.org/x/telemetry v0.0.0-20260625142307-59b4966ccb57 h1:nwGZBCt+FnXUrGsj5vjzAsEmkcaFvd82BbOjECiFYZc=
+golang.org/x/telemetry v0.0.0-20260625142307-59b4966ccb57/go.mod h1:3AWMyWHS+caVoiEXpiq6+tzKA40J4vQT3MYr80ZtQpc=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.1-0.20180807135948-17ff2d5776d2/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.2/go.mod h1:bEr9sfX3Q8Zfm5fL9x+3itogRgK3+ptLWKqgva+5dAk=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
-golang.org/x/text v0.37.0 h1:Cqjiwd9eSg8e0QAkyCaQTNHFIIzWtidPahFWR83rTrc=
-golang.org/x/text v0.37.0/go.mod h1:a5sjxXGs9hsn/AJVwuElvCAo9v8QYLzvavO5z2PiM38=
+golang.org/x/text v0.40.0 h1:Ub2Z6/xjgF1WrYQz2nuITOEegKFtiIy+rieRJ5lHZKs=
+golang.org/x/text v0.40.0/go.mod h1:hpnzDAfGV753zIKo+wk3u1bVKCGPbrnF7+7LBF/UHVY=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20191024005414-555d28b269f0/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -828,8 +830,8 @@ golang.org/x/tools v0.0.0-20200729194436-6467de6f59a7/go.mod h1:njjCfa9FT2d7l9Bc
 golang.org/x/tools v0.0.0-20200804011535-6c149bb5ef0d/go.mod h1:njjCfa9FT2d7l9Bc6FUM5FLjQPp3cFF28FI3qnDFljA=
 golang.org/x/tools v0.0.0-20200806022845-90696ccdc692/go.mod h1:njjCfa9FT2d7l9Bc6FUM5FLjQPp3cFF28FI3qnDFljA=
 golang.org/x/tools v0.0.0-20210106214847-113979e3529a/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
-golang.org/x/tools v0.44.0 h1:UP4ajHPIcuMjT1GqzDWRlalUEoY+uzoZKnhOjbIPD2c=
-golang.org/x/tools v0.44.0/go.mod h1:KA0AfVErSdxRZIsOVipbv3rQhVXTnlU6UhKxHd1seDI=
+golang.org/x/tools v0.47.0 h1:7Kn5x/d1svx/PzryTsqeoZN4TZwqeH5pGWjefhLi/1Q=
+golang.org/x/tools v0.47.0/go.mod h1:dFHnyTvFWY212G+h7ZY4Vsp/K3U4/7W9TyVaAul8uCA=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
```
