# [?] go.mod+docs: bump sqlite version to fix data race

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: lightningnetwork/lnd
Published: 2024-03-19
Source: https://github.com/lightningnetwork/lnd/commit/91ed8cf862252034d39e0f309e15de06c5f4fd50
Type: security-commit

## Details
go.mod+docs: bump sqlite version to fix data race

## Patch
### docs/release-notes/release-notes-0.18.0.md
```diff
@@ -304,6 +304,9 @@
 * [Correct `fmt.Errorf` error wrapping 
   instances](https://github.com/lightningnetwork/lnd/pull/8503)
 
+* Bump sqlite version to [fix a data 
+  race](https://github.com/lightningnetwork/lnd/pull/8567).
+
 ## Breaking Changes
 ## Performance Improvements
 
```

### go.mod
```diff
@@ -59,14 +59,14 @@ require (
 	golang.org/x/exp v0.0.0-20231226003508-02704c960a9b
 	golang.org/x/mobile v0.0.0-20190719004257-d2bd2a29d028
 	golang.org/x/net v0.21.0
-	golang.org/x/sync v0.5.0
+	golang.org/x/sync v0.6.0
 	golang.org/x/term v0.18.0
 	golang.org/x/time v0.0.0-20220224211638-0e9765cccd65
 	google.golang.org/grpc v1.56.3
 	google.golang.org/protobuf v1.33.0
 	gopkg.in/macaroon-bakery.v2 v2.0.1
 	gopkg.in/macaroon.v2 v2.0.0
-	modernc.org/sqlite v1.20.3
+	modernc.org/sqlite v1.29.5
 )
 
 require (
@@ -93,7 +93,7 @@ require (
 	github.com/docker/docker v24.0.7+incompatible // indirect
 	github.com/docker/go-connections v0.4.0 // indirect
 	github.com/docker/go-units v0.5.0 // indirect
-	github.com/dustin/go-humanize v1.0.0 // indirect
+	github.com/dustin/go-humanize v1.0.1 // indirect
 	github.com/fergusstrange/embedded-postgres v1.25.0 // indirect
 	github.com/fsnotify/fsnotify v1.5.4 // indirect
 	github.com/gogo/protobuf v1.3.2 // indirect
@@ -106,6 +106,7 @@ require (
 	github.com/grpc-ecosystem/grpc-gateway v1.16.0 // indirect
 	github.com/hashicorp/errwrap v1.1.0 // indirect
 	github.com/hashicorp/go-multierror v1.1.1 // indirect
+	github.com/hashicorp/golang-lru/v2 v2.0.7 // indirect
 	github.com/imdario/mergo v0.3.12 // indirect
 	github.com/jackc/chunkreader/v2 v2.0.1 // indirect
 	github.com/jackc/pgio v1.0.0 // indirect
@@ -118,7 +119,6 @@ require (
 	github.com/json-iterator/go v1.1.11 // indirect
 	github.com/juju/loggo v0.0.0-20210728185423-eebad3a902c4 // indirect
 	github.com/juju/testing v0.0.0-20220203020004-a0ff61f03494 // indirect
-	github.com/kballard/go-shellquote v0.0.0-20180428030007-95032a82bc51 // indirect
 	github.com/lightninglabs/gozmq v0.0.0-20191113021534-d20a764486bf // indirect
 	github.com/mattn/go-isatty v0.0.16 // indirect
 	github.com/mattn/go-runewidth v0.0.13 // indirect
@@ -127,6 +127,7 @@ require (
 	github.com/moby/term v0.5.0 // indirect
 	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
 	github.com/modern-go/reflect2 v1.0.1 // indirect
+	github.com/ncruces/go-strftime v0.1.9 // indirect
 	github.com/nxadm/tail v1.4.8 // indirect
 	github.com/onsi/gomega v1.26.0 // indirect
 	github.com/opencontainers/go-digest v1.0.0 // indirect
@@ -137,7 +138,7 @@ require (
 	github.com/prometheus/client_model v0.2.0 // indirect
 	github.com/prometheus/common v0.26.0 // indirect
 	github.com/prometheus/procfs v0.6.0 // indirect
-	github.com/remyoudompheng/bigfft v0.0.0-20200410134404-eec4a21b6bb0 // indirect
+	github.com/remyoudompheng/bigfft v0.0.0-20230129092748-24d4a6f8daec // indirect
 	github.com/rivo/uniseg v0.2.0 // indirect
 	github.com/rogpeppe/fastuuid v1.2.0 // indirect
 	github.com/russross/blackfriday/v2 v2.0.1 // indirect
@@ -173,21 +174,18 @@ require (
 	golang.org/x/mod v0.14.0 // indirect
 	golang.org/x/sys v0.18.0 // indirect
 	golang.org/x/text v0.14.0 // indirect
-	golang.org/x/tools v0.16.0 // indirect
+	golang.org/x/tools v0.17.0 // indirect
 	google.golang.org/genproto v0.0.0-20230410155749-daa745c078e1 // indirect
 	gopkg.in/errgo.v1 v1.0.1 // indirect
 	gopkg.in/natefinch/lumberjack.v2 v2.0.0 // indirect
 	gopkg.in/yaml.v2 v2.4.0 // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
-	lukechampine.com/uint128 v1.2.0 // indirect
-	modernc.org/cc/v3 v3.40.0 // indirect
-	modernc.org/ccgo/v3 v3.16.13 // indirect
-	modernc.org/libc v1.22.2 // indirect
-	modernc.org/mathutil v1.5.0 // indirect
-	modernc.org/memory v1.4.0 // indirect
-	modernc.org/opt v0.1.3 // indirect
-	modernc.org/strutil v1.1.3 // indirect
-	modernc.org/token v1.0.1 // indirect
+	modernc.org/gc/v3 v3.0.0-20240107210532-573471604cb6 // indirect
+	modernc.org/libc v1.41.0 // indirect
+	modernc.org/mathutil v1.6.0 // indirect
+	modernc.org/memory v1.7.2 // indirect
+	modernc.org/strutil v1.2.0 // indirect
+	modernc.org/token v1.1.0 // indirect
 	sigs.k8s.io/yaml v1.2.0 // indirect
 )
 
```

### go.sum
```diff
@@ -170,8 +170,8 @@ github.com/docker/go-connections v0.4.0 h1:El9xVISelRB7BuFusrZozjnkIM5YnzCViNKoh
 github.com/docker/go-connections v0.4.0/go.mod h1:Gbd7IOopHjR8Iph03tsViu4nIes5XhDvyHbTtUxmeec=
 github.com/docker/go-units v0.5.0 h1:69rxXcBk27SvSaaxTtLh/8llcHD8vYHT7WSdRZ/jvr4=
 github.com/docker/go-units v0.5.0/go.mod h1:fgPhTUdO+D/Jk86RDLlptpiXQzgHJF7gydDDbaIK4Dk=
-github.com/dustin/go-humanize v1.0.0 h1:VSnTsYCnlFHaM2/igO1h6X3HA71jcobQuxemgkq4zYo=
-github.com/dustin/go-humanize v1.0.0/go.mod h1:HtrtbFcZ19U5GC7JDqmcUSB87Iq5E25KnS6fMYU6eOk=
+github.com/dustin/go-humanize v1.0.1 h1:GzkhY7T5VNhEkwH0PVJgjz+fX1rhBrR7pRT3mDkpeCY=
+github.com/dustin/go-humanize v1.0.1/go.mod h1:Mu1zIs6XwVuF/gI1OepvI0qD18qycQx+mFykh5fBlto=
 github.com/envoyproxy/go-control-plane v0.9.0/go.mod h1:YTl/9mNaCwkRvm6d1a2C3ymFceY/DCBVvsKhRF0iEA4=
 github.com/envoyproxy/go-control-plane v0.9.1-0.20191026205805-5f8ba28d4473/go.mod h1:YTl/9mNaCwkRvm6d1a2C3ymFceY/DCBVvsKhRF0iEA4=
 github.com/envoyproxy/go-control-plane v0.9.4/go.mod h1:6rpuAdCZL397s3pYoYcLgu1mIlRU8Am5FuJP05cCM98=
@@ -294,6 +294,8 @@ github.com/hashicorp/go-multierror v1.1.1 h1:H5DkEtf6CXdFp0N0Em5UCwQpXMWke8IA0+l
 github.com/hashicorp/go-multierror v1.1.1/go.mod h1:iw975J/qwKPdAO1clOe2L8331t/9/fmwbPZ6JB6eMoM=
 github.com/hashicorp/golang-lru v0.5.0/go.mod h1:/m3WP610KZHVQ1SGc6re/UDhFvYD7pJ4Ao+sR/qLZy8=
 github.com/hashicorp/golang-lru v0.5.1/go.mod h1:/m3WP610KZHVQ1SGc6re/UDhFvYD7pJ4Ao+sR/qLZy8=
+github.com/hashicorp/golang-lru/v2 v2.0.7 h1:a+bsQ5rvGLjzHuww6tVxozPZFVghXaHOwFs4luLUK2k=
+github.com/hashicorp/golang-lru/v2 v2.0.7/go.mod h1:QeFd9opnmA6QUJc5vARoKUSoFhyfM2/ZepoAG6RGpeM=
 github.com/hpcloud/tail v1.0.0/go.mod h1:ab1qPbhIpdTxEkNHXyeSf5vhxWSCs/tWer42PpOxQnU=
 github.com/ianlancetaylor/demangle v0.0.0-20181102032728-5e5cf60278f6/go.mod h1:aSSvb/t6k1mPoxDqO4vJh6VOCGPwU4O0C2/Eqndh1Sc=
 github.com/imdario/mergo v0.3.12 h1:b6R2BslTbIEToALKP7LxUvijTsNI9TAe80pLWN2g/HU=
@@ -383,8 +385,6 @@ github.com/juju/utils/v3 v3.0.0-20220130232349-cd7ecef0e94a h1:5ZWDCeCF0RaITrZGe
 github.com/juju/version/v2 v2.0.0-20211007103408-2e8da085dc23 h1:wtEPbidt1VyHlb8RSztU6ySQj29FLsOQiI9XiJhXDM4=
 github.com/julienschmidt/httprouter v1.2.0/go.mod h1:SYymIcj16QtmaHHD7aYtjjsJG7VTCxuUUipMqKk8s4w=
 github.com/julienschmidt/httprouter v1.3.0/go.mod h1:JR6WtHb+2LUe8TCKY3cZOxFyyO8IZAc4RVcycCCAKdM=
-github.com/kballard/go-shellquote v0.0.0-20180428030007-95032a82bc51 h1:Z9n2FFNUXsshfwJMBgNA0RU6/i7WVaAegv3PtuIHPMs=
-github.com/kballard/go-shellquote v0.0.0-20180428030007-95032a82bc51/go.mod h1:CzGEWj7cYgsdH8dAjBGEr58BoE7ScuLd+fwFZ44+/x8=
 github.com/kisielk/errcheck v1.5.0/go.mod h1:pFxgyoBC7bSaBwPgfKdkLd5X25qrDl4LWUI2bnpBCr8=
 github.com/kisielk/gotool v1.0.0/go.mod h1:XhKaO+MFFWcvkIS/tQcRk01m1F5IRFswLeQ+oQHNcck=
 github.com/kkdai/bstream v0.0.0-20161212061736-f391b8402d23/go.mod h1:J+Gs4SYgM6CZQHDETBtE9HaSEkGmuNXF86RwHhHUvq4=
@@ -449,7 +449,7 @@ github.com/mattn/go-isatty v0.0.16 h1:bq3VjFmv/sOjHtdEhmkEV4x1AJtvUvOJ2PFAZ5+peK
 github.com/mattn/go-isatty v0.0.16/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
 github.com/mattn/go-runewidth v0.0.13 h1:lTGmDsbAYt5DmK6OnoV7EuIF1wEIFAcxld6ypU4OSgU=
 github.com/mattn/go-runewidth v0.0.13/go.mod h1:Jdepj2loyihRzMpdS35Xk/zdY8IAYHsh153qUoGf23w=
-github.com/mattn/go-sqlite3 v1.14.16 h1:yOQRA0RpS5PFz/oikGwBEqvAWhWg5ufRz4ETLjwpU1Y=
+github.com/mattn/go-sqlite3 v1.14.22 h1:2gZY6PC6kBnID23Tichd1K+Z0oS6nE/XwU+Vz/5o4kU=
 github.com/matttproud/golang_protobuf_extensions v1.0.1 h1:4hp9jkHxhMHkqkrB3Ix0jegS5sx/RkqARlsWZ6pIwiU=
 github.com/matttproud/golang_protobuf_extensions v1.0.1/go.mod h1:D8He9yQNgCq6Z5Ld7szi9bcBfOoFv/3dc6xSMkL2PC0=
 github.com/miekg/dns v1.1.43 h1:JKfpVSCB84vrAmHzyrsxB5NAr5kLoMXZArPSw7Qlgyg=
@@ -467,6 +467,8 @@ github.com/modern-go/reflect2 v1.0.1/go.mod h1:bx2lNnkwVCuqBIxFjflWJWanXIb3Rllmb
 github.com/morikuni/aec v1.0.0 h1:nP9CBfwrvYnBRgY6qfDQkygYDmYwOilePFkwzv4dU8A=
 github.com/mwitkow/go-conntrack v0.0.0-20161129095857-cc309e4a2223/go.mod h1:qRWi+5nqEBWmkhHvq77mSJWrCKwh8bxhgT7d/eI7P4U=
 github.com/mwitkow/go-conntrack v0.0.0-20190716064945-2f068394615f/go.mod h1:qRWi+5nqEBWmkhHvq77mSJWrCKwh8bxhgT7d/eI7P4U=
+github.com/ncruces/go-strftime v0.1.9 h1:bY0MQC28UADQmHmaF5dgpLmImcShSi2kHU9XLdhx/f4=
+github.com/ncruces/go-strftime v0.1.9/go.mod h1:Fwc5htZGVVkseilnfgOVb9mKy6w1naJmn9CehxcKcls=
 github.com/nxadm/tail v1.4.4/go.mod h1:kenIhsEOeOJmVchQTgglprH7qJGnHDVpk1VPCcaMI8A=
 github.com/nxadm/tail v1.4.8 h1:nPr65rt6Y5JFSKQO7qToXr7pePgD6Gwiw05lkbyAQTE=
 github.com/nxadm/tail v1.4.8/go.mod h1:+ncqLTQzXmGhMZNUePPaPqPvBxHAIsmXswZKocGu+AU=
@@ -516,8 +518,8 @@ github.com/prometheus/procfs v0.0.2/go.mod h1:TjEm7ze935MbeOT/UhFTIMYKhuLP4wbCsT
 github.com/prometheus/procfs v0.1.3/go.mod h1:lV6e/gmhEcM9IjHGsFOCxxuZ+z1YqCvr4OA4YeYWdaU=
 github.com/prometheus/procfs v0.6.0 h1:mxy4L2jP6qMonqmq+aTtOx1ifVWUgG/TAmntgbh3xv4=
 github.com/prometheus/procfs v0.6.0/go.mod h1:cz+aTbrPOrUb4q7XlbU9ygM+/jj0fzG6c1xBZuNvfVA=
-github.com/remyoudompheng/bigfft v0.0.0-20200410134404-eec4a21b6bb0 h1:OdAsTTz6OkFY5QxjkYwrChwuRruF69c169dPK26NUlk=
-github.com/remyoudompheng/bigfft v0.0.0-20200410134404-eec4a21b6bb0/go.mod h1:qqbHyh8v60DhA7CoWK5oRCqLrMHRGoxYCSS9EjAz6Eo=
+github.com/remyoudompheng/bigfft v0.0.0-20230129092748-24d4a6f8daec h1:W09IVJc94icq4NjY3clb7Lk8O1qJ8BdBEF8z0ibU0rE=
+github.com/remyoudompheng/bigfft v0.0.0-20230129092748-24d4a6f8daec/go.mod h1:qqbHyh8v60DhA7CoWK5oRCqLrMHRGoxYCSS9EjAz6Eo=
 github.com/rivo/uniseg v0.2.0 h1:S1pD9weZBuJdFmowNwbpi7BJ8TNftyUImj/0WQi72jY=
 github.com/rivo/uniseg v0.2.0/go.mod h1:J6wj4VEh+S6ZtnVlnTBMWIodfgj8LQOQFoIToxlJtxc=
 github.com/rogpeppe/fastuuid v1.2.0 h1:Ppwyp6VYCF1nvBTXL3trRso7mXMlRrw9ooo375wvi2s=
@@ -749,8 +751,8 @@ golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
-golang.org/x/sync v0.5.0 h1:60k92dhOjHxJkrqnwsfl8KuaHbn/5dl0lUPUklKo3qE=
-golang.org/x/sync v0.5.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
+golang.org/x/sync v0.6.0 h1:5BMeUDZ7vkXGfEr1x9B4bRcTH4lpkTkpdh0T/J+qjbQ=
+golang.org/x/sync v0.6.0/go.mod h1:Czt+wKu1gCyEFDUtn0jG5QVvpJ6rzVqr5aXyt9drQfk=
 golang.org/x/sys v0.0.0-20180816055513-1c9583448a9c/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180905080454-ebe1bf3edb33/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -877,8 +879,8 @@ golang.org/x/tools v0.0.0-20200804011535-6c149bb5ef0d/go.mod h1:njjCfa9FT2d7l9Bc
 golang.org/x/tools v0.0.0-20200825202427-b303f430e36d/go.mod h1:njjCfa9FT2d7l9Bc6FUM5FLjQPp3cFF28FI3qnDFljA=
 golang.org/x/tools v0.0.0-20210106214847-113979e3529a/go.mod h1:emZCQorbCU4vsT4fOWvOPXz4eW1wZW4PmDk9uLelYpA=
 golang.org/x/tools v0.1.3/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
-golang.org/x/tools v0.16.0 h1:GO788SKMRunPIBCXiQyo2AaexLstOrVhuAL5YwsckQM=
-golang.org/x/tools v0.16.0/go.mod h1:kYVVN6I1mBNoB1OX+noeBjbRk4IUEPa7JJ+TJMEooJ0=
+golang.org/x/tools v0.17.0 h1:FvmRgNOcs3kOa+T20R1uhfP9F6HgG2mfxDv1vrx1Htc=
+golang.org/x/tools v0.17.0/go.mod h1:xsh6VxdV005rRVaS6SSAf9oiAqljS7UZUacMZ8Bnsps=
 golang.org/x/xerrors v0.0.0-20190410155217-1f06c39b4373/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20190513163551-3ee3066db522/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
@@ -1002,30 +1004,21 @@ honnef.co/go/tools v0.0.0-20190523083050-ea95bdfd59fc/go.mod h1:rf3lG4BRIbNafJWh
 honnef.co/go/tools v0.0.1-2019.2.3/go.mod h1:a3bituU0lyd329TUQxRnasdCoJDkEUEAqEt0JzvZhAg=
 honnef.co/go/tools v0.0.1-2020.1.3/go.mod h1:X/FiERA/W4tHapMX5mGpAtMSVEeEUOyHaw9vFzvIQ3k=
 honnef.co/go/tools v0.0.1-2020.1.4/go.mod h1:X/FiERA/W4tHapMX5mGpAtMSVEeEUOyHaw9vFzvIQ3k=
-lukechampine.com/uint128 v1.2.0 h1:mBi/5l91vocEN8otkC5bDLhi2KdCticRiwbdB0O+rjI=
-lukechampine.com/uint128 v1.2.0/go.mod h1:c4eWIwlEGaxC/+H1VguhU4PHXNWDCDMUlWdIWl2j1gk=
-modernc.org/cc/v3 v3.40.0 h1:P3g79IUS/93SYhtoeaHW+kRCIrYaxJ27MFPv+7kaTOw=
-modernc.org/cc/v3 v3.40.0/go.mod h1:/bTg4dnWkSXowUO6ssQKnOV0yMVxDYNIsIrzqTFDGH0=
-modernc.org/ccgo/v3 v3.16.13 h1:Mkgdzl46i5F/CNR/Kj80Ri59hC8TKAhZrYSaqvkwzUw=
-modernc.org/ccgo/v3 v3.16.13/go.mod h1:2Quk+5YgpImhPjv2Qsob1DnZ/4som1lJTodubIcoUkY=
-modernc.org/ccorpus v1.11.6 h1:J16RXiiqiCgua6+ZvQot4yUuUy8zxgqbqEEUuGPlISk=
-modernc.org/httpfs v1.0.6 h1:AAgIpFZRXuYnkjftxTAZwMIiwEqAfk8aVB2/oA6nAeM=
-modernc.org/libc v1.22.2 h1:4U7v51GyhlWqQmwCHj28Rdq2Yzwk55ovjFrdPjs8Hb0=
-modernc.org/libc v1.22.2/go.mod h1:uvQavJ1pZ0hIoC/jfqNoMLURIMhKzINIWypNM17puug=
-modernc.org/mathutil v1.5.0 h1:rV0Ko/6SfM+8G+yKiyI830l3Wuz1zRutdslNoQ0kfiQ=
-modernc.org/mathutil v1.5.0/go.mod h1:mZW8CKdRPY1v87qxC/wUdX5O1qDzXMP5TH3wjfpga6E=
-modernc.org/memory v1.4.0 h1:crykUfNSnMAXaOJnnxcSzbUGMqkLWjklJKkBK2nwZwk=
-modernc.org/memory v1.4.0/go.mod h1:PkUhL0Mugw21sHPeskwZW4D6VscE/GQJOnIpCnW6pSU=
-modernc.org/opt v0.1.3 h1:3XOZf2yznlhC+ibLltsDGzABUGVx8J6pnFMS3E4dcq4=
-modernc.org/opt v0.1.3/go.mod h1:WdSiB5evDcignE70guQKxYUl14mgWtbClRi5wmkkTX0=
-modernc.org/sqlite v1.20.3 h1:SqGJMMxjj1PHusLxdYxeQSodg7Jxn9WWkaAQjKrntZs=
-modernc.org/sqlite v1.20.3/go.mod h1:zKcGyrICaxNTMEHSr1HQ2GUraP0j+845GYw37+EyT6A=
-modernc.org/strutil v1.1.3 h1:fNMm+oJklMGYfU9Ylcywl0CO5O6nTfaowNsh2wpPjzY=
-modernc.org/strutil v1.1.3/go.mod h1:MEHNA7PdEnEwLvspRMtWTNnp2nnyvMfkimT1NKNAGbw=
-modernc.org/tcl v1.15.0 h1:oY+JeD11qVVSgVvodMJsu7Edf8tr5E/7tuhF5cNYz34=
-modernc.org/token v1.0.1 h1:A3qvTqOwexpfZZeyI0FeGPDlSWX5pjZu9hF4lU+EKWg=
-modernc.org/token v1.0.1/go.mod h1:UGzOrNV1mAFSEB63lOFHIpNRUVMvYTc6yu1SMY/XTDM=
-modernc.org/z v1.7.0 h1:xkDw/KepgEjeizO2sNco+hqYkU12taxQFqPEmgm1GWE=
+modernc.org/fileutil v1.3.0 h1:gQ5SIzK3H9kdfai/5x41oQiKValumqNTDXMvKo62HvE=
+modernc.org/gc/v3 v3.0.0-20240107210532-573471604cb6 h1:5D53IMaUuA5InSeMu9eJtlQXS2NxAhyWQvkKEgXZhHI=
+modernc.org/gc/v3 v3.0.0-20240107210532-573471604cb6/go.mod h1:Qz0X07sNOR1jWYCrJMEnbW/X55x206Q7Vt4mz6/wHp4=
+modernc.org/libc v1.41.0 h1:g9YAc6BkKlgORsUWj+JwqoB1wU3o4DE3bM3yvA3k+Gk=
+modernc.org/libc v1.41.0/go.mod h1:w0eszPsiXoOnoMJgrXjglgLuDy/bt5RR4y3QzUUeodY=
+modernc.org/mathutil v1.6.0 h1:fRe9+AmYlaej+64JsEEhoWuAYBkOtQiMEU7n/XgfYi4=
+modernc.org/mathutil v1.6.0/go.mod h1:Ui5Q9q1TR2gFm0AQRqQUaBWFLAhQpCwNcuhBOSedWPo=
+modernc.org/memory v1.7.2 h1:Klh90S215mmH8c9gO98QxQFsY+W451E8AnzjoE2ee1E=
+modernc.org/memory v1.7.2/go.mod h1:NO4NVCQy0N7ln+T9ngWqOQfi7ley4vpwvARR+Hjw95E=
+modernc.org/sqlite v1.29.5 h1:8l/SQKAjDtZFo9lkJLdk8g9JEOeYRG4/ghStDCCTiTE=
+modernc.org/sqlite v1.29.5/go.mod h1:S02dvcmm7TnTRvGhv8IGYyLnIt7AS2KPaB1F/71p75U=
+modernc.org/strutil v1.2.0 h1:agBi9dp1I+eOnxXeiZawM8F4LawKv4NzGWSaLfyeNZA=
+modernc.org/strutil v1.2.0/go.mod h1:/mdcBmfOibveCTBxUl5B5l6W+TTH1FXPLHZE6bTosX0=
+modernc.org/token v1.1.0 h1:Xl7Ap9dKaEs5kLoOQeQmPWevfnk/DM5qcLcYlA8ys6Y=
+modernc.org/token v1.1.0/go.mod h1:UGzOrNV1mAFSEB63lOFHIpNRUVMvYTc6yu1SMY/XTDM=
 rsc.io/binaryregexp v0.2.0/go.mod h1:qTv7/COck+e2FymRvadv62gMdZztPaShugOCi3I+8D8=
 rsc.io/quote/v3 v3.1.0/go.mod h1:yEA65RcK8LyAZtP9Kv3t0HmxON59tX3rD+tICJqUlj0=
 rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
```
