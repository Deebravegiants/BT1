# [?] go.mod: upgrade otel to fix CVE-2026-24051 (#3554)

## Summary
Severity: Unknown
Chain: BNB Chain
Component: bnb-chain/bsc
Published: 2026-02-09
Source: https://github.com/bnb-chain/bsc/commit/457539f79fad2accdb98c682b6bf7a5c310761d9
Type: security-commit

## Details
go.mod: upgrade otel to fix CVE-2026-24051 (#3554)

## Patch
### cmd/keeper/go.mod
```diff
@@ -76,7 +76,7 @@ require (
 	github.com/prysmaticlabs/prysm/v5 v5.3.2 // indirect
 	github.com/rcrowley/go-metrics v0.0.0-20201227073835-cf1acfcdf475 // indirect
 	github.com/rivo/uniseg v0.4.7 // indirect
-	github.com/rogpeppe/go-internal v1.13.1 // indirect
+	github.com/rogpeppe/go-internal v1.14.1 // indirect
 	github.com/rs/cors v1.8.2 // indirect
 	github.com/sasha-s/go-deadlock v0.3.1 // indirect
 	github.com/shirou/gopsutil v3.21.11+incompatible // indirect
@@ -94,7 +94,7 @@ require (
 	golang.org/x/exp v0.0.0-20241217172543-b2144cdd0a67 // indirect
 	golang.org/x/net v0.47.0 // indirect
 	golang.org/x/sync v0.18.0 // indirect
-	golang.org/x/sys v0.38.0 // indirect
+	golang.org/x/sys v0.40.0 // indirect
 	golang.org/x/text v0.31.0 // indirect
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20250115164207-1a7da9e5054f // indirect
 	google.golang.org/grpc v1.69.4 // indirect
```

### cmd/keeper/go.sum
```diff
@@ -112,8 +112,8 @@ github.com/go-kit/log v0.2.1 h1:MRVx0/zhvdseW+Gza6N9rVzU/IVzaeE1SFI4raAhmBU=
 github.com/go-kit/log v0.2.1/go.mod h1:NwTd00d/i8cPZ3xOwwiv2PO5MOcx78fFErGNcVmBjv0=
 github.com/go-logfmt/logfmt v0.5.1 h1:otpy5pqBCBZ1ng9RQ0dPu4PN7ba75Y/aA+UpowDyNVA=
 github.com/go-logfmt/logfmt v0.5.1/go.mod h1:WYhtIu8zTZfxdn5+rREduYbwxfcBr/Vr6KEVveWlfTs=
-github.com/go-logr/logr v1.4.2 h1:6pFjapn8bFcIbiKo3XT4j/BhANplGihG6tvd+8rYgrY=
-github.com/go-logr/logr v1.4.2/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
+github.com/go-logr/logr v1.4.3 h1:CjnDlHq8ikf6E492q6eKboGOC0T8CDaOvkHCIg8idEI=
+github.com/go-logr/logr v1.4.3/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
 github.com/go-logr/stdr v1.2.2 h1:hSWxHoqTgW2S2qGc0LTAI563KZ5YKYRhT3MFKZMbjag=
 github.com/go-logr/stdr v1.2.2/go.mod h1:mMo/vtBO5dYbehREoey6XUKy/eSumjCCveDpRre4VKE=
 github.com/go-ole/go-ole v1.2.6/go.mod h1:pprOEPIfldk/42T2oK7lQ4v4JSDwmV0As9GaiUsvbm0=
@@ -141,8 +141,8 @@ github.com/google/btree v1.1.2/go.mod h1:qOPhT0dTNdNzV6Z/lhRX0YXUafgPLFUh+gZMl76
 github.com/google/go-cmp v0.3.0/go.mod h1:8QqcDgzrUqlUb/G2PQTWiueGozuR1884gddMywk6iLU=
 github.com/google/go-cmp v0.3.1/go.mod h1:8QqcDgzrUqlUb/G2PQTWiueGozuR1884gddMywk6iLU=
 github.com/google/go-cmp v0.4.0/go.mod h1:v8dTdLbMG2kIc/vJvl+f65V22dbkXbowE6jgT/gNBxE=
-github.com/google/go-cmp v0.6.0 h1:ofyhxvXcZhMsU5ulbFiLKl/XBFqE1GSq7atu8tAmTRI=
-github.com/google/go-cmp v0.6.0/go.mod h1:17dUlkBOakJ0+DkrSSNjCkIjxS6bF9zb3elmeNGIjoY=
+github.com/google/go-cmp v0.7.0 h1:wk8382ETsv4JYUZwIsn6YpYiWiBsYLSJiTsyBybVuN8=
+github.com/google/go-cmp v0.7.0/go.mod h1:pXiqmnSA92OHEEa9HXL2W4E7lf9JzCmGVUdgjX3N/iU=
 github.com/google/gofuzz v1.2.0 h1:xRy4A+RhZaiKjJ1bPfwQ8sedCA+YS2YcCHW6ec7JMi0=
 github.com/google/gofuzz v1.2.0/go.mod h1:dBl0BpW6vV/+mYPU4Po3pmUjxk6FQPldtuIdl/M65Eg=
 github.com/google/orderedcode v0.0.1 h1:UzfcAexk9Vhv8+9pNOgRu41f16lHq725vPwnSeiG/Us=
@@ -258,8 +258,8 @@ github.com/rivo/uniseg v0.2.0/go.mod h1:J6wj4VEh+S6ZtnVlnTBMWIodfgj8LQOQFoIToxlJ
 github.com/rivo/uniseg v0.4.7 h1:WUdvkW8uEhrYfLC4ZzdpI2ztxP1I582+49Oc5Mq64VQ=
 github.com/rivo/uniseg v0.4.7/go.mod h1:FN3SvrM+Zdj16jyLfmOkMNblXMcoc8DfTHruCPUcx88=
 github.com/rogpeppe/go-internal v1.9.0/go.mod h1:WtVeX8xhTBvf0smdhujwtBcq4Qrzq/fJaraNFVN+nFs=
-github.com/rogpeppe/go-internal v1.13.1 h1:KvO1DLK/DRN07sQ1LQKScxyZJuNnedQ5/wKSR38lUII=
-github.com/rogpeppe/go-internal v1.13.1/go.mod h1:uMEvuHeurkdAXX61udpOXGD/AzZDWNMNyH2VO9fmH0o=
+github.com/rogpeppe/go-internal v1.14.1 h1:UQB4HGPB6osV0SQTLymcB4TgvyWu6ZyliaW0tI/otEQ=
+github.com/rogpeppe/go-internal v1.14.1/go.mod h1:MaRKkUm5W0goXpeCfT7UZI6fk/L7L7so1lCWt35ZSgc=
 github.com/rs/cors v1.8.2 h1:KCooALfAYGs415Cwu5ABvv9n9509fSiG5SQJn/AQo4U=
 github.com/rs/cors v1.8.2/go.mod h1:XyqrcTp5zjWr1wsJ8PIRZssZ8b/WMcMf71DJnit4EMU=
 github.com/russross/blackfriday/v2 v2.1.0 h1:JIOH55/0cWyOuilr9/qlrm0BSXldqnqwMsf35Ld67mk=
@@ -273,8 +273,8 @@ github.com/sirupsen/logrus v1.9.3/go.mod h1:naHLuLoDiP4jHNo9R0sCBMtWGeIprob74mVs
 github.com/stretchr/objx v0.1.0/go.mod h1:HFkY916IF+rwdDfMAkV7OtwuqBVzrE8GR6GFx+wExME=
 github.com/stretchr/testify v1.4.0/go.mod h1:j7eGeouHqKxXV5pUuKE4zz7dFj8WfuZ+81PSLYec5m4=
 github.com/stretchr/testify v1.7.0/go.mod h1:6Fq8oRcR53rry900zMqJjRRixrwX3KX962/h/Wwjteg=
-github.com/stretchr/testify v1.10.0 h1:Xv5erBjTwe/5IxqUQTdXv5kgmIvbHo3QQyRwhJsOfJA=
-github.com/stretchr/testify v1.10.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
+github.com/stretchr/testify v1.11.1 h1:7s2iGBzp5EwR7/aIZr8ao5+dra3wiQyKjjFuvgVKu7U=
+github.com/stretchr/testify v1.11.1/go.mod h1:wZwfW3scLgRK+23gO65QZefKpKQRnfz6sD981Nm4B6U=
 github.com/supranational/blst v0.3.16-0.20250831170142-f48500c1fdbe h1:nbdqkIGOGfUAD54q1s2YBcBz/WcsxCO9HUQ4aGV5hUw=
 github.com/supranational/blst v0.3.16-0.20250831170142-f48500c1fdbe/go.mod h1:jZJtfjgudtNl4en1tzwPIV3KjUnQUvG3/j+w+fVonLw=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 h1:epCh84lMvA70Z7CTTCmYQn2CKbY8j86K7/FAIr141uY=
@@ -301,18 +301,18 @@ github.com/yusufpapurcu/wmi v1.2.3 h1:E1ctvB7uKFMOJw3fdOW32DwGE9I7t++CRUEMKvFoFi
 github.com/yusufpapurcu/wmi v1.2.3/go.mod h1:SBZ9tNy3G9/m5Oi98Zks0QjeHVDvuK0qfxQmPyzfmi0=
 go.etcd.io/bbolt v1.3.9 h1:8x7aARPEXiXbHmtUwAIv7eV2fQFHrLLavdiJ3uzJXoI=
 go.etcd.io/bbolt v1.3.9/go.mod h1:zaO32+Ti0PK1ivdPtgMESzuzL2VPoIG1PCQNvOdo/dE=
-go.opentelemetry.io/auto/sdk v1.1.0 h1:cH53jehLUN6UFLY71z+NDOiNJqDdPRaXzTel0sJySYA=
-go.opentelemetry.io/auto/sdk v1.1.0/go.mod h1:3wSPjt5PWp2RhlCcmmOial7AvC4DQqZb7a7wCow3W8A=
-go.opentelemetry.io/otel v1.34.0 h1:zRLXxLCgL1WyKsPVrgbSdMN4c0FMkDAskSTQP+0hdUY=
-go.opentelemetry.io/otel v1.34.0/go.mod h1:OWFPOQ+h4G8xpyjgqo4SxJYdDQ/qmRH+wivy7zzx9oI=
-go.opentelemetry.io/otel/metric v1.34.0 h1:+eTR3U0MyfWjRDhmFMxe2SsW64QrZ84AOhvqS7Y+PoQ=
-go.opentelemetry.io/otel/metric v1.34.0/go.mod h1:CEDrp0fy2D0MvkXE+dPV7cMi8tWZwX3dmaIhwPOaqHE=
-go.opentelemetry.io/otel/sdk v1.34.0 h1:95zS4k/2GOy069d321O8jWgYsW3MzVV+KuSPKp7Wr1A=
-go.opentelemetry.io/otel/sdk v1.34.0/go.mod h1:0e/pNiaMAqaykJGKbi+tSjWfNNHMTxoC9qANsCzbyxU=
+go.opentelemetry.io/auto/sdk v1.2.1 h1:jXsnJ4Lmnqd11kwkBV2LgLoFMZKizbCi5fNZ/ipaZ64=
+go.opentelemetry.io/auto/sdk v1.2.1/go.mod h1:KRTj+aOaElaLi+wW1kO/DZRXwkF4C5xPbEe3ZiIhN7Y=
+go.opentelemetry.io/otel v1.40.0 h1:oA5YeOcpRTXq6NN7frwmwFR0Cn3RhTVZvXsP4duvCms=
+go.opentelemetry.io/otel v1.40.0/go.mod h1:IMb+uXZUKkMXdPddhwAHm6UfOwJyh4ct1ybIlV14J0g=
+go.opentelemetry.io/otel/metric v1.40.0 h1:rcZe317KPftE2rstWIBitCdVp89A2HqjkxR3c11+p9g=
+go.opentelemetry.io/otel/metric v1.40.0/go.mod h1:ib/crwQH7N3r5kfiBZQbwrTge743UDc7DTFVZrrXnqc=
+go.opentelemetry.io/otel/sdk v1.40.0 h1:KHW/jUzgo6wsPh9At46+h4upjtccTmuZCFAc9OJ71f8=
+go.opentelemetry.io/otel/sdk v1.40.0/go.mod h1:Ph7EFdYvxq72Y8Li9q8KebuYUr2KoeyHx0DRMKrYBUE=
 go.opentelemetry.io/otel/sdk/metric v1.31.0 h1:i9hxxLJF/9kkvfHppyLL55aW7iIJz4JjxTeYusH7zMc=
 go.opentelemetry.io/otel/sdk/metric v1.31.0/go.mod h1:CRInTMVvNhUKgSAMbKyTMxqOBC0zgyxzW55lZzX43Y8=
-go.opentelemetry.io/otel/trace v1.34.0 h1:+ouXS2V8Rd4hp4580a8q23bg0azF2nI8cqLYnC8mh/k=
-go.opentelemetry.io/otel/trace v1.34.0/go.mod h1:Svm7lSjQD7kG7KJ/MUHPVXSDGz2OX4h0M2jHBhmSfRE=
+go.opentelemetry.io/otel/trace v1.40.0 h1:WA4etStDttCSYuhwvEa8OP8I5EWu24lkOzp+ZYblVjw=
+go.opentelemetry.io/otel/trace v1.40.0/go.mod h1:zeAhriXecNGP/s2SEG3+Y8X9ujcJOTqQ5RgdEJcawiA=
 golang.org/x/crypto v0.0.0-20190308221718-c2843e01d9a2/go.mod h1:djNgcEr1/C05ACkg1iLfiJU5Ep61QUkGW8qpdssI0+w=
 golang.org/x/crypto v0.0.0-20190701094942-4def268fd1a4/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
 golang.org/x/crypto v0.0.0-20191011191535-87dc89f01550/go.mod h1:yigFU9vqHzYiE8UmvKecakEJjdnWj3jj499lnFckfCI=
@@ -353,8 +353,8 @@ golang.org/x/sys v0.0.0-20200814200057-3d37ad5750ed/go.mod h1:h1NjWce9XRLGQEsW7w
 golang.org/x/sys v0.0.0-20200930185726-fdedc70b468f/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20220715151400-c0bba94af5f8/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.38.0 h1:3yZWxaJjBmCWXqhN1qh02AkOnCQ1poK6oF+a7xWL6Gc=
-golang.org/x/sys v0.38.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
+golang.org/x/sys v0.40.0 h1:DBZZqJ2Rkml6QMQsZywtnjnnGvHza6BTfYFWY9kjEWQ=
+golang.org/x/sys v0.40.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
 golang.org/x/term v0.37.0 h1:8EGAD0qCmHYZg6J17DvsMy9/wJ7/D/4pV/wfnld5lTU=
 golang.org/x/term v0.37.0/go.mod h1:5pB4lxRNYYVZuTLmy8oR2BH8dflOR+IbTYFD8fi3254=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
```

### go.mod
```diff
@@ -69,7 +69,7 @@ require (
 	github.com/rs/cors v1.8.2
 	github.com/shirou/gopsutil v3.21.11+incompatible
 	github.com/status-im/keycard-go v0.2.0
-	github.com/stretchr/testify v1.10.0
+	github.com/stretchr/testify v1.11.1
 	github.com/supranational/blst v0.3.16-0.20250831170142-f48500c1fdbe
 	github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
 	github.com/tendermint/go-amino v0.14.1
@@ -84,7 +84,7 @@ require (
 	golang.org/x/crypto v0.45.0
 	golang.org/x/exp v0.0.0-20241217172543-b2144cdd0a67
 	golang.org/x/sync v0.18.0
-	golang.org/x/sys v0.38.0
+	golang.org/x/sys v0.40.0
 	golang.org/x/text v0.31.0
 	golang.org/x/time v0.9.0
 	golang.org/x/tools v0.38.0
@@ -150,7 +150,7 @@ require (
 	github.com/go-kit/kit v0.12.0 // indirect
 	github.com/go-kit/log v0.2.1 // indirect
 	github.com/go-logfmt/logfmt v0.5.1 // indirect
-	github.com/go-logr/logr v1.4.2 // indirect
+	github.com/go-logr/logr v1.4.3 // indirect
 	github.com/go-logr/stdr v1.2.2 // indirect
 	github.com/go-ole/go-ole v1.3.0 // indirect
 	github.com/go-playground/locales v0.14.1 // indirect
@@ -163,7 +163,7 @@ require (
 	github.com/gogo/protobuf v1.3.2 // indirect
 	github.com/golang/groupcache v0.0.0-20210331224755-41bb18bfe9da // indirect
 	github.com/golang/protobuf v1.5.4 // indirect
-	github.com/google/go-cmp v0.6.0 // indirect
+	github.com/google/go-cmp v0.7.0 // indirect
 	github.com/google/go-querystring v1.1.0 // indirect
 	github.com/google/gopacket v1.1.19 // indirect
 	github.com/grpc-ecosystem/go-grpc-middleware v1.3.0 // indirect
@@ -270,7 +270,7 @@ require (
 	github.com/raulk/go-watchdog v1.3.0 // indirect
 	github.com/rcrowley/go-metrics v0.0.0-20201227073835-cf1acfcdf475 // indirect
 	github.com/rivo/uniseg v0.4.7 // indirect
-	github.com/rogpeppe/go-internal v1.13.1 // indirect
+	github.com/rogpeppe/go-internal v1.14.1 // indirect
 	github.com/russross/blackfriday/v2 v2.1.0 // indirect
 	github.com/sasha-s/go-deadlock v0.3.1 // indirect
 	github.com/schollz/progressbar/v3 v3.3.4 // indirect
@@ -295,14 +295,14 @@ require (
 	github.com/yusufpapurcu/wmi v1.2.3 // indirect
 	go.etcd.io/bbolt v1.3.9 // indirect
 	go.opencensus.io v0.24.0 // indirect
-	go.opentelemetry.io/auto/sdk v1.1.0 // indirect
+	go.opentelemetry.io/auto/sdk v1.2.1 // indirect
 	go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.59.0 // indirect
-	go.opentelemetry.io/otel v1.34.0 // indirect
+	go.opentelemetry.io/otel v1.40.0 // indirect
 	go.opentelemetry.io/otel/exporters/otlp/otlptrace v1.34.0 // indirect
 	go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp v1.34.0 // indirect
-	go.opentelemetry.io/otel/metric v1.34.0 // indirect
-	go.opentelemetry.io/otel/sdk v1.34.0 // indirect
-	go.opentelemetry.io/otel/trace v1.34.0 // indirect
+	go.opentelemetry.io/otel/metric v1.40.0 // indirect
+	go.opentelemetry.io/otel/sdk v1.40.0 // indirect
+	go.opentelemetry.io/otel/trace v1.40.0 // indirect
 	go.opentelemetry.io/proto/otlp v1.5.0 // indirect
 	go.uber.org/dig v1.18.0 // indirect
 	go.uber.org/fx v1.23.0 // indirect
```

### go.sum
```diff
@@ -362,8 +362,8 @@ github.com/go-logfmt/logfmt v0.5.0/go.mod h1:wCYkCAKZfumFQihp8CzCvQ3paCTfi41vtzG
 github.com/go-logfmt/logfmt v0.5.1 h1:otpy5pqBCBZ1ng9RQ0dPu4PN7ba75Y/aA+UpowDyNVA=
 github.com/go-logfmt/logfmt v0.5.1/go.mod h1:WYhtIu8zTZfxdn5+rREduYbwxfcBr/Vr6KEVveWlfTs=
 github.com/go-logr/logr v1.2.2/go.mod h1:jdQByPbusPIv2/zmleS9BjJVeZ6kBagPoEUsqbVz/1A=
-github.com/go-logr/logr v1.4.2 h1:6pFjapn8bFcIbiKo3XT4j/BhANplGihG6tvd+8rYgrY=
-github.com/go-logr/logr v1.4.2/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
+github.com/go-logr/logr v1.4.3 h1:CjnDlHq8ikf6E492q6eKboGOC0T8CDaOvkHCIg8idEI=
+github.com/go-logr/logr v1.4.3/go.mod h1:9T104GzyrTigFIr8wt5mBrctHMim0Nb2HLGrmQ40KvY=
 github.com/go-logr/stdr v1.2.2 h1:hSWxHoqTgW2S2qGc0LTAI563KZ5YKYRhT3MFKZMbjag=
 github.com/go-logr/stdr v1.2.2/go.mod h1:mMo/vtBO5dYbehREoey6XUKy/eSumjCCveDpRre4VKE=
 github.com/go-ole/go-ole v1.2.6/go.mod h1:pprOEPIfldk/42T2oK7lQ4v4JSDwmV0As9GaiUsvbm0=
@@ -465,8 +465,8 @@ github.com/google/go-cmp v0.5.3/go.mod h1:v8dTdLbMG2kIc/vJvl+f65V22dbkXbowE6jgT/
 github.com/google/go-cmp v0.5.4/go.mod h1:v8dTdLbMG2kIc/vJvl+f65V22dbkXbowE6jgT/gNBxE=
 github.com/google/go-cmp v0.5.8/go.mod h1:17dUlkBOakJ0+DkrSSNjCkIjxS6bF9zb3elmeNGIjoY=
 github.com/google/go-cmp v0.5.9/go.mod h1:17dUlkBOakJ0+DkrSSNjCkIjxS6bF9zb3elmeNGIjoY=
-github.com/google/go-cmp v0.6.0 h1:ofyhxvXcZhMsU5ulbFiLKl/XBFqE1GSq7atu8tAmTRI=
-github.com/google/go-cmp v0.6.0/go.mod h1:17dUlkBOakJ0+DkrSSNjCkIjxS6bF9zb3elmeNGIjoY=
+github.com/google/go-cmp v0.7.0 h1:wk8382ETsv4JYUZwIsn6YpYiWiBsYLSJiTsyBybVuN8=
+github.com/google/go-cmp v0.7.0/go.mod h1:pXiqmnSA92OHEEa9HXL2W4E7lf9JzCmGVUdgjX3N/iU=
 github.com/google/go-github v17.0.0+incompatible/go.mod h1:zLgOLi98H3fifZn+44m+umXrS52loVEgC2AApnigrVQ=
 github.com/google/go-querystring v1.0.0/go.mod h1:odCYkC5MyYFN7vkCjXpyrEuKhc/BUO6wN/zVPAxq5ck=
 github.com/google/go-querystring v1.1.0 h1:AnCroh3fv4ZBgVIf1Iwtovgjaw/GiKJo8M8yD/fhyJ8=
@@ -1016,8 +1016,8 @@ github.com/rogpeppe/fastuuid v0.0.0-20150106093220-6724a57986af/go.mod h1:XWv6So
 github.com/rogpeppe/go-internal v1.3.0/go.mod h1:M8bDsm7K2OlrFYOpmOWEs/qY81heoFRclV5y23lUDJ4=
 github.com/rogpeppe/go-internal v1.6.1/go.mod h1:xXDCJY+GAPziupqXw64V24skbSoqbTEfhy4qGm1nDQc=
 github.com/rogpeppe/go-internal v1.9.0/go.mod h1:WtVeX8xhTBvf0smdhujwtBcq4Qrzq/fJaraNFVN+nFs=
-github.com/rogpeppe/go-internal v1.13.1 h1:KvO1DLK/DRN07sQ1LQKScxyZJuNnedQ5/wKSR38lUII=
-github.com/rogpeppe/go-internal v1.13.1/go.mod h1:uMEvuHeurkdAXX61udpOXGD/AzZDWNMNyH2VO9fmH0o=
+github.com/rogpeppe/go-internal v1.14.1 h1:UQB4HGPB6osV0SQTLymcB4TgvyWu6ZyliaW0tI/otEQ=
+github.com/rogpeppe/go-internal v1.14.1/go.mod h1:MaRKkUm5W0goXpeCfT7UZI6fk/L7L7so1lCWt35ZSgc=
 github.com/rs/cors v1.8.2 h1:KCooALfAYGs415Cwu5ABvv9n9509fSiG5SQJn/AQo4U=
 github.com/rs/cors v1.8.2/go.mod h1:XyqrcTp5zjWr1wsJ8PIRZssZ8b/WMcMf71DJnit4EMU=
 github.com/russross/blackfriday v1.5.2/go.mod h1:JO/DiYxRf+HjHt06OyowR9PTA263kcR/rfWxYHBV53g=
@@ -1101,8 +1101,8 @@ github.com/stretchr/testify v1.8.2/go.mod h1:w2LPCIKwWwSfY2zedu0+kehJoqGctiVI29o
 github.com/stretchr/testify v1.8.3/go.mod h1:sz/lmYIOXD/1dqDmKjjqLyZ2RngseejIcXlSw2iwfAo=
 github.com/stretchr/testify v1.8.4/go.mod h1:sz/lmYIOXD/1dqDmKjjqLyZ2RngseejIcXlSw2iwfAo=
 github.com/stretchr/testify v1.9.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
-github.com/stretchr/testify v1.10.0 h1:Xv5erBjTwe/5IxqUQTdXv5kgmIvbHo3QQyRwhJsOfJA=
-github.com/stretchr/testify v1.10.0/go.mod h1:r2ic/lqez/lEtzL7wO/rwa5dbSLXVDPFyf8C91i36aY=
+github.com/stretchr/testify v1.11.1 h1:7s2iGBzp5EwR7/aIZr8ao5+dra3wiQyKjjFuvgVKu7U=
+github.com/stretchr/testify v1.11.1/go.mod h1:wZwfW3scLgRK+23gO65QZefKpKQRnfz6sD981Nm4B6U=
 github.com/supranational/blst v0.3.16-0.20250831170142-f48500c1fdbe h1:nbdqkIGOGfUAD54q1s2YBcBz/WcsxCO9HUQ4aGV5hUw=
 github.com/supranational/blst v0.3.16-0.20250831170142-f48500c1fdbe/go.mod h1:jZJtfjgudtNl4en1tzwPIV3KjUnQUvG3/j+w+fVonLw=
 github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7 h1:epCh84lMvA70Z7CTTCmYQn2CKbY8j86K7/FAIr141uY=
@@ -1195,24 +1195,24 @@ go.opencensus.io v0.22.4/go.mod h1:yxeiOL68Rb0Xd1ddK5vPZ/oVn4vY4Ynel7k9FzqtOIw=
 go.opencensus.io v0.22.5/go.mod h1:5pWMHQbX5EPX2/62yrJeAkowc+lfs/XD7Uxpq3pI6kk=
 go.opencensus.io v0.24.0 h1:y73uSU6J157QMP2kn2r30vwW1A2W2WFwSCGnAVxeaD0=
 go.opencensus.io v0.24.0/go.mod h1:vNK8G9p7aAivkbmorf4v+7Hgx+Zs0yY+0fOtgBfjQKo=
-go.opentelemetry.io/auto/sdk v1.1.0 h1:cH53jehLUN6UFLY71z+NDOiNJqDdPRaXzTel0sJySYA=
-go.opentelemetry.io/auto/sdk v1.1.0/go.mod h1:3wSPjt5PWp2RhlCcmmOial7AvC4DQqZb7a7wCow3W8A=
+go.opentelemetry.io/auto/sdk v1.2.1 h1:jXsnJ4Lmnqd11kwkBV2LgLoFMZKizbCi5fNZ/ipaZ64=
+go.opentelemetry.io/auto/sdk v1.2.1/go.mod h1:KRTj+aOaElaLi+wW1kO/DZRXwkF4C5xPbEe3ZiIhN7Y=
 go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.59.0 h1:CV7UdSGJt/Ao6Gp4CXckLxVRRsRgDHoI8XjbL3PDl8s=
 go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp v0.59.0/go.mod h1:FRmFuRJfag1IZ2dPkHnEoSFVgTVPUd2qf5Vi69hLb8I=
-go.opentelemetry.io/otel v1.34.0 h1:zRLXxLCgL1WyKsPVrgbSdMN4c0FMkDAskSTQP+0hdUY=
-go.opentelemetry.io/otel v1.34.0/go.mod h1:OWFPOQ+h4G8xpyjgqo4SxJYdDQ/qmRH+wivy7zzx9oI=
+go.opentelemetry.io/otel v1.40.0 h1:oA5YeOcpRTXq6NN7frwmwFR0Cn3RhTVZvXsP4duvCms=
+go.opentelemetry.io/otel v1.40.0/go.mod h1:IMb+uXZUKkMXdPddhwAHm6UfOwJyh4ct1ybIlV14J0g=
 go.opentelemetry.io/otel/exporters/otlp/otlptrace v1.34.0 h1:OeNbIYk/2C15ckl7glBlOBp5+WlYsOElzTNmiPW/x60=
 go.opentelemetry.io/otel/exporters/otlp/otlptrace v1.34.0/go.mod h1:7Bept48yIeqxP2OZ9/AqIpYS94h2or0aB4FypJTc8ZM=
 go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp v1.34.0 h1:BEj3SPM81McUZHYjRS5pEgNgnmzGJ5tRpU5krWnV8Bs=
 go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracehttp v1.34.0/go.mod h1:9cKLGBDzI/F3NoHLQGm4ZrYdIHsvGt6ej6hUowxY0J4=
-go.opentelemetry.io/otel/metric v1.34.0 h1:+eTR3U0MyfWjRDhmFMxe2SsW64QrZ84AOhvqS7Y+PoQ=
-go.opentelemetry.io/otel/metric v1.34.0/go.mod h1:CEDrp0fy2D0MvkXE+dPV7cMi8tWZwX3dmaIhwPOaqHE=
-go.opentelemetry.io/otel/sdk v1.34.0 h1:95zS4k/2GOy069d321O8jWgYsW3MzVV+KuSPKp7Wr1A=
-go.opentelemetry.io/otel/sdk v1.34.0/go.mod h1:0e/pNiaMAqaykJGKbi+tSjWfNNHMTxoC9qANsCzbyxU=
-go.opentelemetry.io/otel/sdk/metric v1.31.0 h1:i9hxxLJF/9kkvfHppyLL55aW7iIJz4JjxTeYusH7zMc=
-go.opentelemetry.io/otel/sdk/metric v1.31.0/go.mod h1:CRInTMVvNhUKgSAMbKyTMxqOBC0zgyxzW55lZzX43Y8=
-go.opentelemetry.io/otel/trace v1.34.0 h1:+ouXS2V8Rd4hp4580a8q23bg0azF2nI8cqLYnC8mh/k=
-go.opentelemetry.io/otel/trace v1.34.0/go.mod h1:Svm7lSjQD7kG7KJ/MUHPVXSDGz2OX4h0M2jHBhmSfRE=
+go.opentelemetry.io/otel/metric v1.40.0 h1:rcZe317KPftE2rstWIBitCdVp89A2HqjkxR3c11+p9g=
+go.opentelemetry.io/otel/metric v1.40.0/go.mod h1:ib/crwQH7N3r5kfiBZQbwrTge743UDc7DTFVZrrXnqc=
+go.opentelemetry.io/otel/sdk v1.40.0 h1:KHW/jUzgo6wsPh9At46+h4upjtccTmuZCFAc9OJ71f8=
+go.opentelemetry.io/otel/sdk v1.40.0/go.mod h1:Ph7EFdYvxq72Y8Li9q8KebuYUr2KoeyHx0DRMKrYBUE=
+go.opentelemetry.io/otel/sdk/metric v1.40.0 h1:mtmdVqgQkeRxHgRv4qhyJduP3fYJRMX4AtAlbuWdCYw=
+go.opentelemetry.io/otel/sdk/metric v1.40.0/go.mod h1:4Z2bGMf0KSK3uRjlczMOeMhKU2rhUqdWNoKcYrtcBPg=
+go.opentelemetry.io/otel/trace v1.40.0 h1:WA4etStDttCSYuhwvEa8OP8I5EWu24lkOzp+ZYblVjw=
+go.opentelemetry.io/otel/trace v1.40.0/go.mod h1:zeAhriXecNGP/s2SEG3+Y8X9ujcJOTqQ5RgdEJcawiA=
 go.opentelemetry.io/proto/otlp v1.5.0 h1:xJvq7gMzB31/d406fB8U5CBdyQGw4P399D1aQWU/3i4=
 go.opentelemetry.io/proto/otlp v1.5.0/go.mod h1:keN8WnHxOy8PG0rQZjJJ5A2ebUoafqWp0eVQ4yIXvJ4=
 go.uber.org/atomic v1.3.2/go.mod h1:gD2HeocX3+yG+ygLZcrzQJaqmWj9AIm7n08wl/qW/PE=
@@ -1481,8 +1481,8 @@ golang.org/x/sys v0.8.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.9.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.11.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.16.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.38.0 h1:3yZWxaJjBmCWXqhN1qh02AkOnCQ1poK6oF+a7xWL6Gc=
-golang.org/x/sys v0.38.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
+golang.org/x/sys v0.40.0 h1:DBZZqJ2Rkml6QMQsZywtnjnnGvHza6BTfYFWY9kjEWQ=
+golang.org/x/sys v0.40.0/go.mod h1:OgkHotnGiDImocRcuBABYBEXf8A9a87e/uXjp9XT3ks=
 golang.org/x/telemetry v0.0.0-20251008203120-078029d740a8 h1:LvzTn0GQhWuvKH/kVRS3R3bVAsdQWI7hvfLHGgh9+lU=
 golang.org/x/telemetry v0.0.0-20251008203120-078029d740a8/go.mod h1:Pi4ztBfryZoJEkyFTI5/Ocsu2jXyDr6iSdgJiYE/uwE=
 golang.org/x/term v0.0.0-20201117132131-f5c789dd3221/go.mod h1:Nr5EML6q2oocZ2LXRh80K7BxOlk5/8JxuGnuhpl+muw=
```
