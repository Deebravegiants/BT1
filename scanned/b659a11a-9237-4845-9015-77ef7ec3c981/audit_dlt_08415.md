# [?] build(deps): bump core to v0.7.0 and fix GHSA-3vp4-m3rf-835h (#16128)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-05-12
Source: https://github.com/cosmos/cosmos-sdk/commit/6c07d59b45053eb0333689e3c15a6b1b2d133c18
Type: security-commit

## Details
build(deps): bump core to v0.7.0 and fix GHSA-3vp4-m3rf-835h (#16128)

## Patch
### go.mod
```diff
@@ -5,7 +5,7 @@ module github.com/cosmos/cosmos-sdk
 require (
 	cosmossdk.io/api v0.4.1
 	cosmossdk.io/collections v0.1.0
-	cosmossdk.io/core v0.6.1
+	cosmossdk.io/core v0.7.0
 	cosmossdk.io/depinject v1.0.0-alpha.3
 	cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4
 	cosmossdk.io/log v1.1.0
@@ -161,22 +161,25 @@ require (
 	nhooyr.io/websocket v1.8.6 // indirect
 )
 
-// Below are the long-lived replace of the Cosmos SDK
+// Below are the short-lived replace of the Cosmos SDK
 replace (
 	// TODO: remove me after collections 0.2. is released.
 	cosmossdk.io/collections => ./collections
-	cosmossdk.io/core => ./core
 	cosmossdk.io/store => ./store
 	// TODO: remove after 0.7.0 release
 	cosmossdk.io/x/tx => ./x/tx
+)
+
+// Below are the long-lived replace of the Cosmos SDK
+replace (
 	// use cosmos fork of keyring
 	github.com/99designs/keyring => github.com/cosmos/keyring v1.2.0
 	// dgrijalva/jwt-go is deprecated and doesn't receive security updates.
 	// TODO: remove it: https://github.com/cosmos/cosmos-sdk/issues/13134
 	github.com/dgrijalva/jwt-go => github.com/golang-jwt/jwt/v4 v4.4.2
-	// Fix upstream GHSA-h395-qcrw-5vmq vulnerability.
+	// Fix upstream GHSA-h395-qcrw-5vmq and GHSA-3vp4-m3rf-835h vulnerabilities.
 	// TODO Remove it: https://github.com/cosmos/cosmos-sdk/issues/10409
-	github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.8.1
+	github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.9.0
 	// Downgraded to avoid bugs in following commits which caused simulations to fail.
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
 )
```

### go.sum
```diff
@@ -37,6 +37,8 @@ cloud.google.com/go/storage v1.10.0/go.mod h1:FLPqc6j+Ki4BU591ie1oL6qBQGu2Bl/tZ9
 cloud.google.com/go/storage v1.14.0/go.mod h1:GrKmX003DSIwi9o29oFT7YDnHYwZoctc3fOKtUw0Xmo=
 cosmossdk.io/api v0.4.1 h1:0ikaYM6GyxTYYcfBiyR8YnLCfhNnhKpEFnaSepCTmqg=
 cosmossdk.io/api v0.4.1/go.mod h1:jR7k5ok90LxW2lFUXvd8Vpo/dr4PpiyVegxdm7b1ZdE=
+cosmossdk.io/core v0.7.0 h1:GFss3qt2P9p23Cz24NnqLkslzb8n+B75A24x1JgJJp0=
+cosmossdk.io/core v0.7.0/go.mod h1:36hP0ZH/8ipsjzfcp0yKU4bqQXUGhS0/m1krWFCtwCc=
 cosmossdk.io/depinject v1.0.0-alpha.3 h1:6evFIgj//Y3w09bqOUOzEpFj5tsxBqdc5CfkO7z+zfw=
 cosmossdk.io/depinject v1.0.0-alpha.3/go.mod h1:eRbcdQ7MRpIPEM5YUJh8k97nxHpYbc3sMUnEtt8HPWU=
 cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4 h1:rOy7iw7HlwKc5Af5qIHLXdBx/F98o6du/I/WGwOW6eA=
@@ -111,6 +113,9 @@ github.com/btcsuite/btcd/btcutil v1.1.2 h1:XLMbX8JQEiwMcYft2EGi8zPUkoa0abKIU6/BJ
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1 h1:q0rUy8C/TYNBQS1+CGKw68tLOFYSNEs0TFnxxnS9+4U=
 github.com/bufbuild/protocompile v0.4.0 h1:LbFKd2XowZvQ/kajzguUp2DC9UEIQhIq77fZZlaQsNA=
 github.com/bufbuild/protocompile v0.4.0/go.mod h1:3v93+mbWn/v3xzN+31nwkJfrEpAUwp+BagBSZWx+TP8=
+github.com/bytedance/sonic v1.5.0/go.mod h1:ED5hyg4y6t3/9Ku1R6dU/4KyJ48DZ4jPhfY1O2AihPM=
+github.com/bytedance/sonic v1.8.0 h1:ea0Xadu+sHlu7x5O3gKhRpQ1IKiMrSiHttPF0ybECuA=
+github.com/bytedance/sonic v1.8.0/go.mod h1:i736AoUSYt75HyZLoJW9ERYxcy6eaN6h4BZXU064P/U=
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
 github.com/cenkalti/backoff v2.2.1+incompatible h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=
 github.com/cenkalti/backoff v2.2.1+incompatible/go.mod h1:90ReRw6GdpyfrHakVjL/QHaoyV4aDUVVkXQJJJ3NXXM=
@@ -123,6 +128,9 @@ github.com/cespare/xxhash v1.1.0/go.mod h1:XrSqR1VqqWfGrhpAt58auRo0WTKS1nRRg3ghf
 github.com/cespare/xxhash/v2 v2.1.1/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/cespare/xxhash/v2 v2.2.0 h1:DC2CZ1Ep5Y4k3ZQ899DldepgrayRUGE6BBZ/cd9Cj44=
 github.com/cespare/xxhash/v2 v2.2.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
+github.com/chenzhuoyu/base64x v0.0.0-20211019084208-fb5309c8db06/go.mod h1:DH46F32mSOjUmXrMHnKwZdA8wcEefY7UVqBKYGjpdQY=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311 h1:qSGYFH7+jGhDF8vLC+iwCD4WpbV1EBDSzWkJODFLams=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311/go.mod h1:b583jCggY9gE99b6G5LEC39OIiVsWj+R97kbl5odCEk=
 github.com/chzyer/logex v1.1.10/go.mod h1:+Ywpsq7O8HXn0nuIou7OrIPyXbp3wmkHB+jjWRnGsAI=
 github.com/chzyer/logex v1.2.1 h1:XHDu3E6q+gdHgsdTPH6ImJMIp436vR6MPtH8gP05QzM=
 github.com/chzyer/logex v1.2.1/go.mod h1:JLbx6lG2kDbNRFnfkgvh4eRJRPX1QCoOIWomwysCBrQ=
@@ -275,8 +283,8 @@ github.com/getsentry/sentry-go v0.20.0/go.mod h1:lc76E2QywIyW8WuBnwl8Lc4bkmQH4+w
 github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
 github.com/gin-contrib/sse v0.1.0 h1:Y/yl/+YNO8GZSjAhjMsSuLt29uWRFHdHYUb5lYOV9qE=
 github.com/gin-contrib/sse v0.1.0/go.mod h1:RHrZQHXnP2xjPF+u1gW/2HnVO7nvIa9PG3Gm+fLHvGI=
-github.com/gin-gonic/gin v1.8.1 h1:4+fr/el88TOO3ewCmQr8cx/CtZ/umlIRIs5M4NTNjf8=
-github.com/gin-gonic/gin v1.8.1/go.mod h1:ji8BvRH1azfM+SYow9zQ6SZMvR8qOMZHmsCuWR9tTTk=
+github.com/gin-gonic/gin v1.9.0 h1:OjyFBKICoexlu99ctXNR2gg+c5pKrKMuyjgARg9qeY8=
+github.com/gin-gonic/gin v1.9.0/go.mod h1:W1Me9+hsUSyj3CePGrd1/QrKJMSJ1Tu/0hFEH89961k=
 github.com/go-check/check v0.0.0-20180628173108-788fd7840127/go.mod h1:9ES+weclKsC9YodN5RgxqK/VD9HM9JsCSh7rNhMZE98=
 github.com/go-errors/errors v1.0.1/go.mod h1:f4zRHt4oKfwPJE5k8C9vpYG+aDHdBFUsgrm6/TyX73Q=
 github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
@@ -297,13 +305,13 @@ github.com/go-logfmt/logfmt v0.5.0/go.mod h1:wCYkCAKZfumFQihp8CzCvQ3paCTfi41vtzG
 github.com/go-logfmt/logfmt v0.6.0 h1:wGYYu3uicYdqXVgoYbvnkrPVXkuLM1p1ifugDMEdRi4=
 github.com/go-logfmt/logfmt v0.6.0/go.mod h1:WYhtIu8zTZfxdn5+rREduYbwxfcBr/Vr6KEVveWlfTs=
 github.com/go-martini/martini v0.0.0-20170121215854-22fa46961aab/go.mod h1:/P9AEU963A2AYjv4d1V5eVL1CQbEJq6aCNHDDjibzu8=
-github.com/go-playground/assert/v2 v2.0.1/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
-github.com/go-playground/locales v0.14.0 h1:u50s323jtVGugKlcYeyzC0etD1HifMjqmJqb8WugfUU=
-github.com/go-playground/locales v0.14.0/go.mod h1:sawfccIbzZTqEDETgFXqTho0QybSa7l++s0DH+LDiLs=
-github.com/go-playground/universal-translator v0.18.0 h1:82dyy6p4OuJq4/CByFNOn/jYrnRPArHwAcmLoJZxyho=
-github.com/go-playground/universal-translator v0.18.0/go.mod h1:UvRDBj+xPUEGrFYl+lu/H90nyDXpg0fqeB/AQUGNTVA=
-github.com/go-playground/validator/v10 v10.10.0/go.mod h1:74x4gJWsvQexRdW8Pn3dXSGrTK4nAUsbPlLADvpJkos=
-github.com/go-playground/validator/v10 v10.11.1 h1:prmOlTVv+YjZjmRmNSF3VmspqJIxJWXmqUsHwfTRRkQ=
+github.com/go-playground/assert/v2 v2.2.0/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
+github.com/go-playground/locales v0.14.1 h1:EWaQ/wswjilfKLTECiXz7Rh+3BjFhfDFKv/oXslEjJA=
+github.com/go-playground/locales v0.14.1/go.mod h1:hxrqLVvrK65+Rwrd5Fc6F2O76J/NuW9t0sjnWqG1slY=
+github.com/go-playground/universal-translator v0.18.1 h1:Bcnm0ZwsGyWbCzImXv+pAJnYK9S473LQFuzCbDbfSFY=
+github.com/go-playground/universal-translator v0.18.1/go.mod h1:xekY+UJKNuX9WP91TpwSH2VMlDf28Uj24BCp08ZFTUY=
+github.com/go-playground/validator/v10 v10.11.2 h1:q3SHpufmypg+erIExEKUmsgmhDTyhcJ38oeKGACXohU=
+github.com/go-playground/validator/v10 v10.11.2/go.mod h1:NieE624vt4SCTJtD87arVLvdmjPAeV8BQlHtMnw9D7s=
 github.com/go-sql-driver/mysql v1.4.0/go.mod h1:zAC/RDZ24gD3HViQzih4MyKcchzm+sOG5ZlKdlhCg5w=
 github.com/go-stack/stack v1.8.0/go.mod h1:v0f6uXyyMGvRgIKkXu+yp6POWl0qKG85gN/melR3HDY=
 github.com/gobwas/httphead v0.0.0-20180130184737-2c6c146eadee h1:s+21KNqlpePfkah2I+gwHF8xmJWRjooY+5248k6m4A0=
@@ -312,8 +320,8 @@ github.com/gobwas/pool v0.2.0 h1:QEmUOlnSjWtnpRGHF3SauEiOsy82Cup83Vf2LcMlnc8=
 github.com/gobwas/pool v0.2.0/go.mod h1:q8bcK0KcYlCgd9e7WYLm9LpyS+YeLd8JVDW6WezmKEw=
 github.com/gobwas/ws v1.0.2 h1:CoAavW/wd/kulfZmSIBt6p24n4j7tHgNVCjsfHVNUbo=
 github.com/gobwas/ws v1.0.2/go.mod h1:szmBTxLgaFppYjEmNtny/v3w89xOydFnnZMcgRRu/EM=
-github.com/goccy/go-json v0.9.7/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
-github.com/goccy/go-json v0.9.11 h1:/pAaQDLHEoCq/5FFmSKBswWmK6H0e8g4159Kc/X/nqk=
+github.com/goccy/go-json v0.10.0 h1:mXKd9Qw4NuzShiRlOXKews24ufknHO7gx30lsDyokKA=
+github.com/goccy/go-json v0.10.0/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2 h1:ZpnhV/YsD2/4cESfV5+Hoeu/iUR3ruzNvZ+yQfO03a0=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2/go.mod h1:bBOAhwG1umN6/6ZUMtDFBMQR8jRg9O75tm9K00oMsK4=
 github.com/godbus/dbus/v5 v5.0.4/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
@@ -538,7 +546,10 @@ github.com/klauspost/compress v1.11.7/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYs
 github.com/klauspost/compress v1.12.3/go.mod h1:8dP1Hq4DHOhN9w426knH3Rhby4rFm6D8eO+e+Dq5Gzg=
 github.com/klauspost/compress v1.16.5 h1:IFV2oUNUzZaz+XyusxpLzpzS8Pt5rh0Z16For/djlyI=
 github.com/klauspost/compress v1.16.5/go.mod h1:ntbaceVETuRiXiv4DpjP66DpAtAGkEQskQzEyD//IeE=
+github.com/klauspost/cpuid v1.2.1 h1:vJi+O/nMdFt0vqm8NZBI6wzALWdA2X+egi0ogNyrC/w=
 github.com/klauspost/cpuid v1.2.1/go.mod h1:Pj4uuM528wm8OyEC2QMXAi2YiTZ96dNQPGgoMS4s3ek=
+github.com/klauspost/cpuid/v2 v2.0.9 h1:lgaqFMSdTdQYdZ04uHyN2d/eKdOMyi2YLSvlQIBFYa4=
+github.com/klauspost/cpuid/v2 v2.0.9/go.mod h1:FInQzS24/EEf25PyTYn52gqo7WaD8xa0213Md/qVLRg=
 github.com/konsorten/go-windows-terminal-sequences v1.0.1/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/konsorten/go-windows-terminal-sequences v1.0.3/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/kr/fs v0.1.0/go.mod h1:FFnZGqtBN9Gxj7eW1uZ42v5BccTP0vu6NEaFoC2HwRg=
@@ -585,6 +596,7 @@ github.com/mattn/go-isatty v0.0.9/go.mod h1:YNRxwqDuOph6SZLI9vUUz6OYw3QyUt7WiY2y
 github.com/mattn/go-isatty v0.0.12/go.mod h1:cbi8OIDigv2wuxKPP5vlRcQ1OAZbq2CE4Kysco4FUpU=
 github.com/mattn/go-isatty v0.0.14/go.mod h1:7GGIvUiUoEMVVmxf/4nioHXj79iQHKdU27kJ6hsGG94=
 github.com/mattn/go-isatty v0.0.16/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
+github.com/mattn/go-isatty v0.0.17/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
 github.com/mattn/go-isatty v0.0.18 h1:DOKFKCQ7FNG2L1rbrmstDN4QVRdS89Nkh85u68Uwp98=
 github.com/mattn/go-isatty v0.0.18/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
 github.com/mattn/go-runewidth v0.0.2/go.mod h1:LwmH8dsx7+W8Uxz3IHJYH5QSwggIsqBzpuz5H//U1FU=
@@ -671,7 +683,7 @@ github.com/pascaldekloe/goe v0.1.0 h1:cBOtyMzM9HTpWjXfbbunk26uA6nG3a8n06Wieeh0Mw
 github.com/pascaldekloe/goe v0.1.0/go.mod h1:lzWF7FIEvWOWxwDKqyGYQf6ZUaNfKdP144TG7ZOy1lc=
 github.com/pborman/uuid v1.2.0/go.mod h1:X/NO0urCmaxf9VXbdlT7C2Yzkj2IKimNn4k+gtPdI/k=
 github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
-github.com/pelletier/go-toml/v2 v2.0.1/go.mod h1:r9LEWfGN8R5k0VXJ+0BkIe7MYkRdwZOjgMj2KwnJFUo=
+github.com/pelletier/go-toml/v2 v2.0.6/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/pelletier/go-toml/v2 v2.0.7 h1:muncTPStnKRos5dpVKULv2FVd4bMOhNePj9CjgDb8Us=
 github.com/pelletier/go-toml/v2 v2.0.7/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/performancecopilot/speed v3.0.0+incompatible/go.mod h1:/CLtqpZ5gBg1M9iaPbIdPPGyKcA8hKdoy6hAWba7Yac=
@@ -819,13 +831,14 @@ github.com/tidwall/btree v1.6.0 h1:LDZfKfQIBHGHWSwckhXI0RPSXzlo+KYdjK7FWSqOzzg=
 github.com/tidwall/btree v1.6.0/go.mod h1:twD9XRA5jj9VUQGELzDO4HPQTNJsoWWfYEL+EUQ2cKY=
 github.com/tmc/grpc-websocket-proxy v0.0.0-20170815181823-89b8d40f7ca8/go.mod h1:ncp9v5uamzpCO7NfCPTXjqaC+bZgJeR0sMTm6dMHP7U=
 github.com/tv42/httpunix v0.0.0-20150427012821-b75d8614f926/go.mod h1:9ESjWnEqriFuLhtthL60Sar/7RFoluCcXsuvEwTV5KM=
+github.com/twitchyliquid64/golang-asm v0.15.1 h1:SU5vSMR7hnwNxj24w34ZyCi/FmDZTkS4MhqMhdFk5YI=
+github.com/twitchyliquid64/golang-asm v0.15.1/go.mod h1:a1lVb/DtPvCB8fslRZhAngC2+aY1QWCk3Cedj/Gdt08=
+github.com/ugorji/go v1.1.7 h1:/68gy2h+1mWMrwZFeD1kQialdSzAb432dtpeJ42ovdo=
 github.com/ugorji/go v1.1.7/go.mod h1:kZn38zHttfInRq0xu/PH0az30d+z6vm202qpg1oXVMw=
-github.com/ugorji/go v1.2.7 h1:qYhyWUUd6WbiM+C6JZAUkIJt/1WrjzNHY9+KCIjVqTo=
-github.com/ugorji/go v1.2.7/go.mod h1:nF9osbDWLy6bDVv/Rtoh6QgnvNDpmCalQV5urGCCS6M=
 github.com/ugorji/go/codec v0.0.0-20181204163529-d75b2dcb6bc8/go.mod h1:VFNgLljTbGfSG7qAOspJ7OScBnGdDN/yBr0sguwnwf0=
 github.com/ugorji/go/codec v1.1.7/go.mod h1:Ax+UKWsSmolVDwsd+7N3ZtXu+yMGCf907BLYF3GoBXY=
-github.com/ugorji/go/codec v1.2.7 h1:YPXUKf7fYbp/y8xloBqZOw2qaVggbfwMlI8WM3wZUJ0=
-github.com/ugorji/go/codec v1.2.7/go.mod h1:WGN1fab3R1fzQlVQTkfxVtIBhWDRqOviHU95kRgeqEY=
+github.com/ugorji/go/codec v1.2.9 h1:rmenucSohSTiyL09Y+l2OCk+FrMxGMzho2+tjr5ticU=
+github.com/ugorji/go/codec v1.2.9/go.mod h1:UNopzCgEMSXjBc6AOMqYvWC1ktqTAfzJZUZgYf6w6lg=
 github.com/urfave/cli v1.20.0/go.mod h1:70zkFmudgCuE/ngEzBv17Jvp/497gISqfk5gWijbERA=
 github.com/urfave/cli v1.22.1/go.mod h1:Gos4lmkARVdJ6EkW0WaNv/tZAAMe9V7XWyB60NtXRu0=
 github.com/urfave/negroni v1.0.0/go.mod h1:Meg73S6kFm/4PpbYdq35yYWoCZ9mS/YSx+lKnmiohz4=
@@ -848,6 +861,7 @@ github.com/yuin/goldmark v1.1.27/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9de
 github.com/yuin/goldmark v1.1.32/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.2.1/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.3.5/go.mod h1:mwnBkeHKe2W/ZEtQ+71ViKU8L12m81fl3OWwC1Zlc8k=
+github.com/yuin/goldmark v1.4.13/go.mod h1:6yULJ656Px+3vBD8DxQVa3kxgyrAnzto9xy5taEt/CY=
 github.com/zondax/hid v0.9.1 h1:gQe66rtmyZ8VeGFcOpbuH3r7erYtNEAezCAYu8LdkJo=
 github.com/zondax/hid v0.9.1/go.mod h1:l5wttcP0jwtdLjqjMMWFVEE7d1zO0jvSPA9OPZxWpEM=
 github.com/zondax/ledger-go v0.14.1 h1:Pip65OOl4iJ84WTpA4BKChvOufMhhbxED3BaihoZN4c=
@@ -877,6 +891,8 @@ go.uber.org/tools v0.0.0-20190618225709-2cfd321de3ee/go.mod h1:vJERXedbb3MVM5f9E
 go.uber.org/zap v1.10.0/go.mod h1:vwi/ZaCAaUcBkycHslxD9B2zi4UTXhF60s6SWpuDF0Q=
 go.uber.org/zap v1.13.0/go.mod h1:zwrFLgMcdUuIBviXEYEH1YKNaOBnKXsx2IPda5bBwHM=
 go.uber.org/zap v1.18.1/go.mod h1:xg/QME4nWcxGxrpdeYfq7UvYrLh66cuVKdrbD1XF/NI=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670 h1:18EFjUmQOcUvxNYSkA6jO9VAiXCnxFY6NyDX0bHDmkU=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670/go.mod h1:5om86z9Hs0C8fWVUuoMHwpExlXzs5Tkyp9hOrfG7pp8=
 golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181029021203-45a5f77698d3/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181203042331-505ab145d0a9/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
@@ -891,9 +907,9 @@ golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPh
 golang.org/x/crypto v0.0.0-20200728195943-123391ffb6de/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20210421170649-83a5a9bb288b/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
-golang.org/x/crypto v0.0.0-20210711020723-a769d52b0f97/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20210921155107-089bfa567519/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20211108221036-ceb1ce70b4fa/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
+golang.org/x/crypto v0.5.0/go.mod h1:NK/OQwhpMQP3MwtdjgLlYHnH9ebylxKWv3e0fK+mkQU=
 golang.org/x/crypto v0.9.0 h1:LF6fAI+IutBocDJ2OT0Q1g8plpYljMZ4+lty+dsqw3g=
 golang.org/x/crypto v0.9.0/go.mod h1:yrmDGqONDYtNj3tH8X9dzUun2m2lzPa9ngI6/RUPGR0=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
@@ -934,6 +950,7 @@ golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.2/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
+golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4/go.mod h1:jJ57K6gSWd91VN4djpZkiMVwK6gcyfeH4XE8wZrZaV4=
 golang.org/x/mod v0.8.0 h1:LUYupSeNrTNCGzR/hVBk2NHZO4hXcVaW1k4Qx7rjPx8=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -983,6 +1000,9 @@ golang.org/x/net v0.0.0-20210405180319-a5a99cb37ef4/go.mod h1:p54w0d4576C0XHj96b
 golang.org/x/net v0.0.0-20210805182204-aaa1db679c0d/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20211008194852-3b03d305991f/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
+golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
+golang.org/x/net v0.5.0/go.mod h1:DivGGAXEgPSlEBzxGzZI+ZLohi+xUj054jfeKui00ws=
+golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
 golang.org/x/net v0.10.0 h1:X2//UzNDwYmtCLn7To6G58Wr6f5ahEAQgKNzv9Y951M=
 golang.org/x/net v0.10.0/go.mod h1:0qNGK6F8kojg2nk9dLZ2mShWaEBan6FAoqfSigmmuDg=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
@@ -1005,6 +1025,7 @@ golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
+golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.2.0 h1:PUR+T4wwASmuSTYdKjYHI5TD22Wy5ogLU5qZCOLxBrI=
 golang.org/x/sync v0.2.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -1073,7 +1094,6 @@ golang.org/x/sys v0.0.0-20210423185535-09eb48e85fd7/go.mod h1:h1NjWce9XRLGQEsW7w
 golang.org/x/sys v0.0.0-20210510120138-977fb7262007/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210615035016-665e8c7367d1/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210630005230-0f9fa26af87c/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20210806184541-e5e7981a1069/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210809222454-d867a43fc93e/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210819135213-f52c844e1c1c/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210927094055-39ccf1dd6fa6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
@@ -1084,14 +1104,20 @@ golang.org/x/sys v0.0.0-20220209214540-3681064d5158/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220310020820-b874c991c1a5/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220315194320-039c03cc5b86/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220503163025-988cb79eb6c6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.0.0-20220722155257-8c9f86f7a55f/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20221010170243-090e33056c14/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.4.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.5.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.8.0 h1:EBmGv8NaZBZTWvrbjNoL6HVt+IVy3QDQpJs7VRIw3tU=
 golang.org/x/sys v0.8.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
+golang.org/x/term v0.4.0/go.mod h1:9P2UbLfCdcvo3p/nzKvsmas4TnlujnuoV9hGgYzW1lQ=
+golang.org/x/term v0.5.0/go.mod h1:jMB1sMXY+tzblOD4FWmEbocvup2/aLOaQEp7JmGp78k=
 golang.org/x/term v0.8.0 h1:n5xxQn2i3PC0yLAbjTpNT85q/Kgzcr2gIoX9OrJUols=
 golang.org/x/term v0.8.0/go.mod h1:xPskH00ivmX89bAKVGSKKtLOWNx2+17Eiy94tnKShWo=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1103,6 +1129,9 @@ golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
+golang.org/x/text v0.3.8/go.mod h1:E6s5w1FMmriuDzIBO73fBruAKo1PCIq6d2Q6DHfQ8WQ=
+golang.org/x/text v0.6.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/text v0.9.0 h1:2sjJmO8cDvYveuX97RDLsxlyUxLl+GHoLxBiRdHllBE=
 golang.org/x/text v0.9.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -1171,6 +1200,7 @@ golang.org/x/tools v0.0.0-20210108195828-e2f9c7f1fc8e/go.mod h1:emZCQorbCU4vsT4f
 golang.org/x/tools v0.1.0/go.mod h1:xkSsbof2nBLbhDlRMhhhyNLN/zl3eTqcnHD5viDpcZ0=
 golang.org/x/tools v0.1.1/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.3/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
+golang.org/x/tools v0.1.12/go.mod h1:hNGJHUnrk76NpqgfD5Aqm5Crs+Hm0VOH/i9J2+nxYbc=
 golang.org/x/tools v0.6.0 h1:BOw41kyTf3PuCW1pVQf8+Cyg8pMlkYB1oo9iJ6D/lKM=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
@@ -1293,7 +1323,6 @@ google.golang.org/protobuf v1.25.0/go.mod h1:9JNX74DMeImyA3h4bdi1ymwjUzf21/xIlba
 google.golang.org/protobuf v1.26.0-rc.1/go.mod h1:jlhhOSvTdKEhbULTjvd4ARK9grFBp09yW+WbY/TyQbw=
 google.golang.org/protobuf v1.26.0/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
 google.golang.org/protobuf v1.27.1/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
-google.golang.org/protobuf v1.28.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 google.golang.org/protobuf v1.28.1/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 google.golang.org/protobuf v1.30.0 h1:kPPoIgf3TsEvrm0PFe15JQ+570QVxYzEvvHqChK+cng=
 google.golang.org/protobuf v1.30.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
@@ -1346,6 +1375,7 @@ nhooyr.io/websocket v1.8.6/go.mod h1:B70DZP8IakI65RVQ51MsWP/8jndNma26DVA/nFSCgW0
 pgregory.net/rapid v0.5.7 h1:p7/XbOgyFY1I/3Q12UTXfos70VZTcgc3WeoyiEru5cs=
 pgregory.net/rapid v0.5.7/go.mod h1:PY5XlDGj0+V1FCq0o192FdRhpKHGTRIWBgqjDBTrq04=
 rsc.io/binaryregexp v0.2.0/go.mod h1:qTv7/COck+e2FymRvadv62gMdZztPaShugOCi3I+8D8=
+rsc.io/pdf v0.1.1/go.mod h1:n8OzWcQ6Sp37PL01nO98y4iUCRdTGarVfzxY20ICaU4=
 rsc.io/quote/v3 v3.1.0/go.mod h1:yEA65RcK8LyAZtP9Kv3t0HmxON59tX3rD+tICJqUlj0=
 rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
 sigs.k8s.io/yaml v1.1.0/go.mod h1:UJmg0vDUVViEyp3mgSv9WPwZCDxu4rQW1olrI1uml+o=
```

### simapp/go.mod
```diff
@@ -5,7 +5,7 @@ go 1.20
 require (
 	cosmossdk.io/api v0.4.1
 	cosmossdk.io/client/v2 v2.0.0-20230309163709-87da587416ba
-	cosmossdk.io/core v0.6.2-0.20230323161322-ccd8d40119e4
+	cosmossdk.io/core v0.7.0
 	cosmossdk.io/depinject v1.0.0-alpha.3
 	cosmossdk.io/log v1.1.0
 	cosmossdk.io/math v1.0.0
@@ -198,29 +198,28 @@ replace (
 	// TODO tag all extracted modules after SDK refactor
 	cosmossdk.io/api => ../api
 	cosmossdk.io/client/v2 => ../client/v2
+	// TODO: remove me after collections 0.2. is released.
+	cosmossdk.io/collections => ../collections
 	cosmossdk.io/store => ../store
 	cosmossdk.io/tools/confix => ../tools/confix
 	cosmossdk.io/tools/rosetta => ../tools/rosetta
 	cosmossdk.io/x/evidence => ../x/evidence
 	cosmossdk.io/x/feegrant => ../x/feegrant
 	cosmossdk.io/x/nft => ../x/nft
+	// TODO: remove after 0.7.0 release
+	cosmossdk.io/x/tx => ../x/tx
 	cosmossdk.io/x/upgrade => ../x/upgrade
 )
 
 // Below are the long-lived replace of the SimApp
 replace (
-	// TODO: remove me after collections 0.2. is released.
-	cosmossdk.io/collections => ../collections
-	cosmossdk.io/core => ../core
-	// TODO: remove after 0.7.0 release
-	cosmossdk.io/x/tx => ../x/tx
 	// use cosmos fork of keyring
 	github.com/99designs/keyring => github.com/cosmos/keyring v1.2.0
 	// Simapp always use the latest version of the cosmos-sdk
 	github.com/cosmos/cosmos-sdk => ../.
-	// Fix upstream GHSA-h395-qcrw-5vmq vulnerability.
+	// Fix upstream GHSA-h395-qcrw-5vmq and GHSA-3vp4-m3rf-835h vulnerabilities.
 	// TODO Remove it: https://github.com/cosmos/cosmos-sdk/issues/10409
-	github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.8.1
+	github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.9.0
 	// Downgraded to avoid bugs in following commits which caused simulations to fail.
 	github.com/syndtr/goleveldb => github.com/syndtr/goleveldb v1.0.1-0.20210819022825-2ae1ddf74ef7
 )
```

### simapp/go.sum
```diff
@@ -188,6 +188,8 @@ cloud.google.com/go/webrisk v1.4.0/go.mod h1:Hn8X6Zr+ziE2aNd8SliSDWpEnSS1u4R9+xX
 cloud.google.com/go/webrisk v1.5.0/go.mod h1:iPG6fr52Tv7sGk0H6qUFzmL3HHZev1htXuWDEEsqMTg=
 cloud.google.com/go/workflows v1.6.0/go.mod h1:6t9F5h/unJz41YqfBmqSASJSXccBLtD1Vwf+KmJENM0=
 cloud.google.com/go/workflows v1.7.0/go.mod h1:JhSrZuVZWuiDfKEFxU0/F1PQjmpnpcoISEXH2bcHC3M=
+cosmossdk.io/core v0.7.0 h1:GFss3qt2P9p23Cz24NnqLkslzb8n+B75A24x1JgJJp0=
+cosmossdk.io/core v0.7.0/go.mod h1:36hP0ZH/8ipsjzfcp0yKU4bqQXUGhS0/m1krWFCtwCc=
 cosmossdk.io/depinject v1.0.0-alpha.3 h1:6evFIgj//Y3w09bqOUOzEpFj5tsxBqdc5CfkO7z+zfw=
 cosmossdk.io/depinject v1.0.0-alpha.3/go.mod h1:eRbcdQ7MRpIPEM5YUJh8k97nxHpYbc3sMUnEtt8HPWU=
 cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4 h1:rOy7iw7HlwKc5Af5qIHLXdBx/F98o6du/I/WGwOW6eA=
@@ -266,6 +268,9 @@ github.com/btcsuite/btcd/btcec/v2 v2.3.2/go.mod h1:zYzJ8etWJQIv1Ogk7OzpWjowwOdXY
 github.com/btcsuite/btcd/btcutil v1.1.2 h1:XLMbX8JQEiwMcYft2EGi8zPUkoa0abKIU6/BJSRsjzQ=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1 h1:q0rUy8C/TYNBQS1+CGKw68tLOFYSNEs0TFnxxnS9+4U=
 github.com/bufbuild/protocompile v0.4.0 h1:LbFKd2XowZvQ/kajzguUp2DC9UEIQhIq77fZZlaQsNA=
+github.com/bytedance/sonic v1.5.0/go.mod h1:ED5hyg4y6t3/9Ku1R6dU/4KyJ48DZ4jPhfY1O2AihPM=
+github.com/bytedance/sonic v1.8.0 h1:ea0Xadu+sHlu7x5O3gKhRpQ1IKiMrSiHttPF0ybECuA=
+github.com/bytedance/sonic v1.8.0/go.mod h1:i736AoUSYt75HyZLoJW9ERYxcy6eaN6h4BZXU064P/U=
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
 github.com/cenkalti/backoff v2.2.1+incompatible h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=
 github.com/cenkalti/backoff v2.2.1+incompatible/go.mod h1:90ReRw6GdpyfrHakVjL/QHaoyV4aDUVVkXQJJJ3NXXM=
@@ -279,6 +284,9 @@ github.com/cespare/xxhash/v2 v2.1.1/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XL
 github.com/cespare/xxhash/v2 v2.2.0 h1:DC2CZ1Ep5Y4k3ZQ899DldepgrayRUGE6BBZ/cd9Cj44=
 github.com/cespare/xxhash/v2 v2.2.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/cheggaaa/pb v1.0.27/go.mod h1:pQciLPpbU0oxA0h+VJYYLxO+XeDQb5pZijXscXHm81s=
+github.com/chenzhuoyu/base64x v0.0.0-20211019084208-fb5309c8db06/go.mod h1:DH46F32mSOjUmXrMHnKwZdA8wcEefY7UVqBKYGjpdQY=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311 h1:qSGYFH7+jGhDF8vLC+iwCD4WpbV1EBDSzWkJODFLams=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311/go.mod h1:b583jCggY9gE99b6G5LEC39OIiVsWj+R97kbl5odCEk=
 github.com/chzyer/logex v1.1.10/go.mod h1:+Ywpsq7O8HXn0nuIou7OrIPyXbp3wmkHB+jjWRnGsAI=
 github.com/chzyer/logex v1.2.1 h1:XHDu3E6q+gdHgsdTPH6ImJMIp436vR6MPtH8gP05QzM=
 github.com/chzyer/logex v1.2.1/go.mod h1:JLbx6lG2kDbNRFnfkgvh4eRJRPX1QCoOIWomwysCBrQ=
@@ -440,8 +448,8 @@ github.com/getsentry/sentry-go v0.20.0/go.mod h1:lc76E2QywIyW8WuBnwl8Lc4bkmQH4+w
 github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
 github.com/gin-contrib/sse v0.1.0 h1:Y/yl/+YNO8GZSjAhjMsSuLt29uWRFHdHYUb5lYOV9qE=
 github.com/gin-contrib/sse v0.1.0/go.mod h1:RHrZQHXnP2xjPF+u1gW/2HnVO7nvIa9PG3Gm+fLHvGI=
-github.com/gin-gonic/gin v1.8.1 h1:4+fr/el88TOO3ewCmQr8cx/CtZ/umlIRIs5M4NTNjf8=
-github.com/gin-gonic/gin v1.8.1/go.mod h1:ji8BvRH1azfM+SYow9zQ6SZMvR8qOMZHmsCuWR9tTTk=
+github.com/gin-gonic/gin v1.9.0 h1:OjyFBKICoexlu99ctXNR2gg+c5pKrKMuyjgARg9qeY8=
+github.com/gin-gonic/gin v1.9.0/go.mod h1:W1Me9+hsUSyj3CePGrd1/QrKJMSJ1Tu/0hFEH89961k=
 github.com/go-check/check v0.0.0-20180628173108-788fd7840127/go.mod h1:9ES+weclKsC9YodN5RgxqK/VD9HM9JsCSh7rNhMZE98=
 github.com/go-errors/errors v1.0.1/go.mod h1:f4zRHt4oKfwPJE5k8C9vpYG+aDHdBFUsgrm6/TyX73Q=
 github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
@@ -462,13 +470,13 @@ github.com/go-logfmt/logfmt v0.5.0/go.mod h1:wCYkCAKZfumFQihp8CzCvQ3paCTfi41vtzG
 github.com/go-logfmt/logfmt v0.6.0 h1:wGYYu3uicYdqXVgoYbvnkrPVXkuLM1p1ifugDMEdRi4=
 github.com/go-logfmt/logfmt v0.6.0/go.mod h1:WYhtIu8zTZfxdn5+rREduYbwxfcBr/Vr6KEVveWlfTs=
 github.com/go-martini/martini v0.0.0-20170121215854-22fa46961aab/go.mod h1:/P9AEU963A2AYjv4d1V5eVL1CQbEJq6aCNHDDjibzu8=
-github.com/go-playground/assert/v2 v2.0.1/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
-github.com/go-playground/locales v0.14.0 h1:u50s323jtVGugKlcYeyzC0etD1HifMjqmJqb8WugfUU=
-github.com/go-playground/locales v0.14.0/go.mod h1:sawfccIbzZTqEDETgFXqTho0QybSa7l++s0DH+LDiLs=
-github.com/go-playground/universal-translator v0.18.0 h1:82dyy6p4OuJq4/CByFNOn/jYrnRPArHwAcmLoJZxyho=
-github.com/go-playground/universal-translator v0.18.0/go.mod h1:UvRDBj+xPUEGrFYl+lu/H90nyDXpg0fqeB/AQUGNTVA=
-github.com/go-playground/validator/v10 v10.10.0/go.mod h1:74x4gJWsvQexRdW8Pn3dXSGrTK4nAUsbPlLADvpJkos=
-github.com/go-playground/validator/v10 v10.11.1 h1:prmOlTVv+YjZjmRmNSF3VmspqJIxJWXmqUsHwfTRRkQ=
+github.com/go-playground/assert/v2 v2.2.0/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
+github.com/go-playground/locales v0.14.1 h1:EWaQ/wswjilfKLTECiXz7Rh+3BjFhfDFKv/oXslEjJA=
+github.com/go-playground/locales v0.14.1/go.mod h1:hxrqLVvrK65+Rwrd5Fc6F2O76J/NuW9t0sjnWqG1slY=
+github.com/go-playground/universal-translator v0.18.1 h1:Bcnm0ZwsGyWbCzImXv+pAJnYK9S473LQFuzCbDbfSFY=
+github.com/go-playground/universal-translator v0.18.1/go.mod h1:xekY+UJKNuX9WP91TpwSH2VMlDf28Uj24BCp08ZFTUY=
+github.com/go-playground/validator/v10 v10.11.2 h1:q3SHpufmypg+erIExEKUmsgmhDTyhcJ38oeKGACXohU=
+github.com/go-playground/validator/v10 v10.11.2/go.mod h1:NieE624vt4SCTJtD87arVLvdmjPAeV8BQlHtMnw9D7s=
 github.com/go-sql-driver/mysql v1.4.0/go.mod h1:zAC/RDZ24gD3HViQzih4MyKcchzm+sOG5ZlKdlhCg5w=
 github.com/go-stack/stack v1.8.0/go.mod h1:v0f6uXyyMGvRgIKkXu+yp6POWl0qKG85gN/melR3HDY=
 github.com/gobwas/httphead v0.0.0-20180130184737-2c6c146eadee h1:s+21KNqlpePfkah2I+gwHF8xmJWRjooY+5248k6m4A0=
@@ -477,8 +485,8 @@ github.com/gobwas/pool v0.2.0 h1:QEmUOlnSjWtnpRGHF3SauEiOsy82Cup83Vf2LcMlnc8=
 github.com/gobwas/pool v0.2.0/go.mod h1:q8bcK0KcYlCgd9e7WYLm9LpyS+YeLd8JVDW6WezmKEw=
 github.com/gobwas/ws v1.0.2 h1:CoAavW/wd/kulfZmSIBt6p24n4j7tHgNVCjsfHVNUbo=
 github.com/gobwas/ws v1.0.2/go.mod h1:szmBTxLgaFppYjEmNtny/v3w89xOydFnnZMcgRRu/EM=
-github.com/goccy/go-json v0.9.7/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
-github.com/goccy/go-json v0.9.11 h1:/pAaQDLHEoCq/5FFmSKBswWmK6H0e8g4159Kc/X/nqk=
+github.com/goccy/go-json v0.10.0 h1:mXKd9Qw4NuzShiRlOXKews24ufknHO7gx30lsDyokKA=
+github.com/goccy/go-json v0.10.0/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2 h1:ZpnhV/YsD2/4cESfV5+Hoeu/iUR3ruzNvZ+yQfO03a0=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2/go.mod h1:bBOAhwG1umN6/6ZUMtDFBMQR8jRg9O75tm9K00oMsK4=
 github.com/godbus/dbus/v5 v5.0.4/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
@@ -745,7 +753,10 @@ github.com/klauspost/compress v1.12.3/go.mod h1:8dP1Hq4DHOhN9w426knH3Rhby4rFm6D8
 github.com/klauspost/compress v1.15.11/go.mod h1:QPwzmACJjUTFsnSHH934V6woptycfrDDJnH7hvFVbGM=
 github.com/klauspost/compress v1.16.5 h1:IFV2oUNUzZaz+XyusxpLzpzS8Pt5rh0Z16For/djlyI=
 github.com/klauspost/compress v1.16.5/go.mod h1:ntbaceVETuRiXiv4DpjP66DpAtAGkEQskQzEyD//IeE=
+github.com/klauspost/cpuid v1.2.1 h1:vJi+O/nMdFt0vqm8NZBI6wzALWdA2X+egi0ogNyrC/w=
 github.com/klauspost/cpuid v1.2.1/go.mod h1:Pj4uuM528wm8OyEC2QMXAi2YiTZ96dNQPGgoMS4s3ek=
+github.com/klauspost/cpuid/v2 v2.0.9 h1:lgaqFMSdTdQYdZ04uHyN2d/eKdOMyi2YLSvlQIBFYa4=
+github.com/klauspost/cpuid/v2 v2.0.9/go.mod h1:FInQzS24/EEf25PyTYn52gqo7WaD8xa0213Md/qVLRg=
 github.com/konsorten/go-windows-terminal-sequences v1.0.1/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/konsorten/go-windows-terminal-sequences v1.0.3/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/kr/fs v0.1.0/go.mod h1:FFnZGqtBN9Gxj7eW1uZ42v5BccTP0vu6NEaFoC2HwRg=
@@ -792,6 +803,7 @@ github.com/mattn/go-isatty v0.0.9/go.mod h1:YNRxwqDuOph6SZLI9vUUz6OYw3QyUt7WiY2y
 github.com/mattn/go-isatty v0.0.12/go.mod h1:cbi8OIDigv2wuxKPP5vlRcQ1OAZbq2CE4Kysco4FUpU=
 github.com/mattn/go-isatty v0.0.14/go.mod h1:7GGIvUiUoEMVVmxf/4nioHXj79iQHKdU27kJ6hsGG94=
 github.com/mattn/go-isatty v0.0.16/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
+github.com/mattn/go-isatty v0.0.17/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
 github.com/mattn/go-isatty v0.0.18 h1:DOKFKCQ7FNG2L1rbrmstDN4QVRdS89Nkh85u68Uwp98=
 github.com/mattn/go-isatty v0.0.18/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
 github.com/mattn/go-runewidth v0.0.2/go.mod h1:LwmH8dsx7+W8Uxz3IHJYH5QSwggIsqBzpuz5H//U1FU=
@@ -879,7 +891,7 @@ github.com/pascaldekloe/goe v0.1.0 h1:cBOtyMzM9HTpWjXfbbunk26uA6nG3a8n06Wieeh0Mw
 github.com/pascaldekloe/goe v0.1.0/go.mod h1:lzWF7FIEvWOWxwDKqyGYQf6ZUaNfKdP144TG7ZOy1lc=
 github.com/pborman/uuid v1.2.0/go.mod h1:X/NO0urCmaxf9VXbdlT7C2Yzkj2IKimNn4k+gtPdI/k=
 github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
-github.com/pelletier/go-toml/v2 v2.0.1/go.mod h1:r9LEWfGN8R5k0VXJ+0BkIe7MYkRdwZOjgMj2KwnJFUo=
+github.com/pelletier/go-toml/v2 v2.0.6/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/pelletier/go-toml/v2 v2.0.7 h1:muncTPStnKRos5dpVKULv2FVd4bMOhNePj9CjgDb8Us=
 github.com/pelletier/go-toml/v2 v2.0.7/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/performancecopilot/speed v3.0.0+incompatible/go.mod h1:/CLtqpZ5gBg1M9iaPbIdPPGyKcA8hKdoy6hAWba7Yac=
@@ -1027,13 +1039,14 @@ github.com/tidwall/btree v1.6.0 h1:LDZfKfQIBHGHWSwckhXI0RPSXzlo+KYdjK7FWSqOzzg=
 github.com/tidwall/btree v1.6.0/go.mod h1:twD9XRA5jj9VUQGELzDO4HPQTNJsoWWfYEL+EUQ2cKY=
 github.com/tmc/grpc-websocket-proxy v0.0.0-20170815181823-89b8d40f7ca8/go.mod h1:ncp9v5uamzpCO7NfCPTXjqaC+bZgJeR0sMTm6dMHP7U=
 github.com/tv42/httpunix v0.0.0-20150427012821-b75d8614f926/go.mod h1:9ESjWnEqriFuLhtthL60Sar/7RFoluCcXsuvEwTV5KM=
+github.com/twitchyliquid64/golang-asm v0.15.1 h1:SU5vSMR7hnwNxj24w34ZyCi/FmDZTkS4MhqMhdFk5YI=
+github.com/twitchyliquid64/golang-asm v0.15.1/go.mod h1:a1lVb/DtPvCB8fslRZhAngC2+aY1QWCk3Cedj/Gdt08=
+github.com/ugorji/go v1.1.7 h1:/68gy2h+1mWMrwZFeD1kQialdSzAb432dtpeJ42ovdo=
 github.com/ugorji/go v1.1.7/go.mod h1:kZn38zHttfInRq0xu/PH0az30d+z6vm202qpg1oXVMw=
-github.com/ugorji/go v1.2.7 h1:qYhyWUUd6WbiM+C6JZAUkIJt/1WrjzNHY9+KCIjVqTo=
-github.com/ugorji/go v1.2.7/go.mod h1:nF9osbDWLy6bDVv/Rtoh6QgnvNDpmCalQV5urGCCS6M=
 github.com/ugorji/go/codec v0.0.0-20181204163529-d75b2dcb6bc8/go.mod h1:VFNgLljTbGfSG7qAOspJ7OScBnGdDN/yBr0sguwnwf0=
 github.com/ugorji/go/codec v1.1.7/go.mod h1:Ax+UKWsSmolVDwsd+7N3ZtXu+yMGCf907BLYF3GoBXY=
-github.com/ugorji/go/codec v1.2.7 h1:YPXUKf7fYbp/y8xloBqZOw2qaVggbfwMlI8WM3wZUJ0=
-github.com/ugorji/go/codec v1.2.7/go.mod h1:WGN1fab3R1fzQlVQTkfxVtIBhWDRqOviHU95kRgeqEY=
+github.com/ugorji/go/codec v1.2.9 h1:rmenucSohSTiyL09Y+l2OCk+FrMxGMzho2+tjr5ticU=
+github.com/ugorji/go/codec v1.2.9/go.mod h1:UNopzCgEMSXjBc6AOMqYvWC1ktqTAfzJZUZgYf6w6lg=
 github.com/ulikunitz/xz v0.5.10/go.mod h1:nbz6k7qbPmH4IRqmfOplQw/tblSgqTqBwxkY0oWt/14=
 github.com/ulikunitz/xz v0.5.11 h1:kpFauv27b6ynzBNT/Xy+1k+fK4WswhN/6PN5WhFAGw8=
 github.com/ulikunitz/xz v0.5.11/go.mod h1:nbz6k7qbPmH4IRqmfOplQw/tblSgqTqBwxkY0oWt/14=
@@ -1092,6 +1105,8 @@ go.uber.org/tools v0.0.0-20190618225709-2cfd321de3ee/go.mod h1:vJERXedbb3MVM5f9E
 go.uber.org/zap v1.10.0/go.mod h1:vwi/ZaCAaUcBkycHslxD9B2zi4UTXhF60s6SWpuDF0Q=
 go.uber.org/zap v1.13.0/go.mod h1:zwrFLgMcdUuIBviXEYEH1YKNaOBnKXsx2IPda5bBwHM=
 go.uber.org/zap v1.18.1/go.mod h1:xg/QME4nWcxGxrpdeYfq7UvYrLh66cuVKdrbD1XF/NI=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670 h1:18EFjUmQOcUvxNYSkA6jO9VAiXCnxFY6NyDX0bHDmkU=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670/go.mod h1:5om86z9Hs0C8fWVUuoMHwpExlXzs5Tkyp9hOrfG7pp8=
 golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181029021203-45a5f77698d3/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181203042331-505ab145d0a9/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
@@ -1106,9 +1121,9 @@ golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPh
 golang.org/x/crypto v0.0.0-20200728195943-123391ffb6de/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20210421170649-83a5a9bb288b/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
-golang.org/x/crypto v0.0.0-20210711020723-a769d52b0f97/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20210921155107-089bfa567519/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20211108221036-ceb1ce70b4fa/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
+golang.org/x/crypto v0.5.0/go.mod h1:NK/OQwhpMQP3MwtdjgLlYHnH9ebylxKWv3e0fK+mkQU=
 golang.org/x/crypto v0.9.0 h1:LF6fAI+IutBocDJ2OT0Q1g8plpYljMZ4+lty+dsqw3g=
 golang.org/x/crypto v0.9.0/go.mod h1:yrmDGqONDYtNj3tH8X9dzUun2m2lzPa9ngI6/RUPGR0=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
@@ -1214,6 +1229,8 @@ golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug
 golang.org/x/net v0.0.0-20220909164309-bea034e7d591/go.mod h1:YDH+HFinaLZZlnHAfSS6ZXJJ9M9t4Dl22yv3iI2vPwk=
 golang.org/x/net v0.0.0-20221014081412-f15817d10f9b/go.mod h1:YDH+HFinaLZZlnHAfSS6ZXJJ9M9t4Dl22yv3iI2vPwk=
 golang.org/x/net v0.1.0/go.mod h1:Cx3nUiGt4eDBEyega/BKRp+/AlGL8hYe7U9odMt2Cco=
+golang.org/x/net v0.5.0/go.mod h1:DivGGAXEgPSlEBzxGzZI+ZLohi+xUj054jfeKui00ws=
+golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
 golang.org/x/net v0.10.0 h1:X2//UzNDwYmtCLn7To6G58Wr6f5ahEAQgKNzv9Y951M=
 golang.org/x/net v0.10.0/go.mod h1:0qNGK6F8kojg2nk9dLZ2mShWaEBan6FAoqfSigmmuDg=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
@@ -1362,12 +1379,16 @@ golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20221010170243-090e33056c14/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.4.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.5.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.8.0 h1:EBmGv8NaZBZTWvrbjNoL6HVt+IVy3QDQpJs7VRIw3tU=
 golang.org/x/sys v0.8.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/term v0.1.0/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
+golang.org/x/term v0.4.0/go.mod h1:9P2UbLfCdcvo3p/nzKvsmas4TnlujnuoV9hGgYzW1lQ=
+golang.org/x/term v0.5.0/go.mod h1:jMB1sMXY+tzblOD4FWmEbocvup2/aLOaQEp7JmGp78k=
 golang.org/x/term v0.8.0 h1:n5xxQn2i3PC0yLAbjTpNT85q/Kgzcr2gIoX9OrJUols=
 golang.org/x/term v0.8.0/go.mod h1:xPskH00ivmX89bAKVGSKKtLOWNx2+17Eiy94tnKShWo=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1379,7 +1400,10 @@ golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
+golang.org/x/text v0.3.8/go.mod h1:E6s5w1FMmriuDzIBO73fBruAKo1PCIq6d2Q6DHfQ8WQ=
 golang.org/x/text v0.4.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.6.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/text v0.9.0 h1:2sjJmO8cDvYveuX97RDLsxlyUxLl+GHoLxBiRdHllBE=
 golang.org/x/text v0.9.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -1745,6 +1769,7 @@ nhooyr.io/websocket v1.8.6/go.mod h1:B70DZP8IakI65RVQ51MsWP/8jndNma26DVA/nFSCgW0
 pgregory.net/rapid v0.5.7 h1:p7/XbOgyFY1I/3Q12UTXfos70VZTcgc3WeoyiEru5cs=
 pgregory.net/rapid v0.5.7/go.mod h1:PY5XlDGj0+V1FCq0o192FdRhpKHGTRIWBgqjDBTrq04=
 rsc.io/binaryregexp v0.2.0/go.mod h1:qTv7/COck+e2FymRvadv62gMdZztPaShugOCi3I+8D8=
+rsc.io/pdf v0.1.1/go.mod h1:n8OzWcQ6Sp37PL01nO98y4iUCRdTGarVfzxY20ICaU4=
 rsc.io/quote/v3 v3.1.0/go.mod h1:yEA65RcK8LyAZtP9Kv3t0HmxON59tX3rD+tICJqUlj0=
 rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
 sigs.k8s.io/yaml v1.1.0/go.mod h1:UJmg0vDUVViEyp3mgSv9WPwZCDxu4rQW1olrI1uml+o=
```

### tests/go.mod
```diff
@@ -4,7 +4,7 @@ go 1.20
 
 require (
 	cosmossdk.io/api v0.4.1
-	cosmossdk.io/core v0.6.2-0.20230323161322-ccd8d40119e4
+	cosmossdk.io/core v0.7.0
 	cosmossdk.io/depinject v1.0.0-alpha.3
 	cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4
 	cosmossdk.io/log v1.1.0
@@ -193,26 +193,25 @@ require (
 replace (
 	// TODO tag all extracted modules after SDK refactor
 	cosmossdk.io/api => ../api
+	// TODO: remove me after collections v0.2.0 is released
+	cosmossdk.io/collections => ../collections
 	cosmossdk.io/store => ../store
 	cosmossdk.io/x/evidence => ../x/evidence
 	cosmossdk.io/x/feegrant => ../x/feegrant
 	cosmossdk.io/x/nft => ../x/nft
+	// TODO: remove after 0.7.0 release
+	cosmossdk.io/x/tx => ../x/tx
 	cosmossdk.io/x/upgrade => ../x/upgrade
 )
 
 // Below are the long-lived replace for tests.
 replace (
-	// TODO: remove me after collections v0.2.0 is released
-	cosmossdk.io/collections => ../collections
-	cosmossdk.io/core => ../core
 	// We always want to test against the latest version of the simapp.
 	cosmossdk.io/simapp => ../simapp
-	// TODO: remove after 0.7.0 release
-	cosmossdk.io/x/tx => ../x/tx
 	github.com/99designs/keyring => github.com/cosmos/keyring v1.2.0
 	// We always want to test against the latest version of the SDK.
 	github.com/cosmos/cosmos-sdk => ../.
-	// Fix upstream GHSA-h395-qcrw-5vmq vulnerability.
+	// Fix upstream GHSA-h395-qcrw-5vmq and GHSA-3vp4-m3rf-835h vulnerabilities.
 	// TODO Remove it: https://github.com/cosmos/cosmos-sdk/issues/10409
-	github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.8.1
+	github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.9.0
 )
```

### tests/go.sum
```diff
@@ -190,6 +190,8 @@ cloud.google.com/go/workflows v1.6.0/go.mod h1:6t9F5h/unJz41YqfBmqSASJSXccBLtD1V
 cloud.google.com/go/workflows v1.7.0/go.mod h1:JhSrZuVZWuiDfKEFxU0/F1PQjmpnpcoISEXH2bcHC3M=
 cosmossdk.io/client/v2 v2.0.0-20230309163709-87da587416ba h1:LuPHCncU2KLMNPItFECs709uo46I9wSu2fAWYVCx+/U=
 cosmossdk.io/client/v2 v2.0.0-20230309163709-87da587416ba/go.mod h1:SXdwqO7cN5htalh/lhXWP8V4zKtBrhhcSTU+ytuEtmM=
+cosmossdk.io/core v0.7.0 h1:GFss3qt2P9p23Cz24NnqLkslzb8n+B75A24x1JgJJp0=
+cosmossdk.io/core v0.7.0/go.mod h1:36hP0ZH/8ipsjzfcp0yKU4bqQXUGhS0/m1krWFCtwCc=
 cosmossdk.io/depinject v1.0.0-alpha.3 h1:6evFIgj//Y3w09bqOUOzEpFj5tsxBqdc5CfkO7z+zfw=
 cosmossdk.io/depinject v1.0.0-alpha.3/go.mod h1:eRbcdQ7MRpIPEM5YUJh8k97nxHpYbc3sMUnEtt8HPWU=
 cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4 h1:rOy7iw7HlwKc5Af5qIHLXdBx/F98o6du/I/WGwOW6eA=
@@ -268,6 +270,9 @@ github.com/btcsuite/btcd/btcec/v2 v2.3.2/go.mod h1:zYzJ8etWJQIv1Ogk7OzpWjowwOdXY
 github.com/btcsuite/btcd/btcutil v1.1.2 h1:XLMbX8JQEiwMcYft2EGi8zPUkoa0abKIU6/BJSRsjzQ=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1 h1:q0rUy8C/TYNBQS1+CGKw68tLOFYSNEs0TFnxxnS9+4U=
 github.com/bufbuild/protocompile v0.4.0 h1:LbFKd2XowZvQ/kajzguUp2DC9UEIQhIq77fZZlaQsNA=
+github.com/bytedance/sonic v1.5.0/go.mod h1:ED5hyg4y6t3/9Ku1R6dU/4KyJ48DZ4jPhfY1O2AihPM=
+github.com/bytedance/sonic v1.8.0 h1:ea0Xadu+sHlu7x5O3gKhRpQ1IKiMrSiHttPF0ybECuA=
+github.com/bytedance/sonic v1.8.0/go.mod h1:i736AoUSYt75HyZLoJW9ERYxcy6eaN6h4BZXU064P/U=
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
 github.com/cenkalti/backoff v2.2.1+incompatible h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=
 github.com/cenkalti/backoff v2.2.1+incompatible/go.mod h1:90ReRw6GdpyfrHakVjL/QHaoyV4aDUVVkXQJJJ3NXXM=
@@ -281,6 +286,9 @@ github.com/cespare/xxhash/v2 v2.1.1/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XL
 github.com/cespare/xxhash/v2 v2.2.0 h1:DC2CZ1Ep5Y4k3ZQ899DldepgrayRUGE6BBZ/cd9Cj44=
 github.com/cespare/xxhash/v2 v2.2.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/cheggaaa/pb v1.0.27/go.mod h1:pQciLPpbU0oxA0h+VJYYLxO+XeDQb5pZijXscXHm81s=
+github.com/chenzhuoyu/base64x v0.0.0-20211019084208-fb5309c8db06/go.mod h1:DH46F32mSOjUmXrMHnKwZdA8wcEefY7UVqBKYGjpdQY=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311 h1:qSGYFH7+jGhDF8vLC+iwCD4WpbV1EBDSzWkJODFLams=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311/go.mod h1:b583jCggY9gE99b6G5LEC39OIiVsWj+R97kbl5odCEk=
 github.com/chzyer/logex v1.1.10/go.mod h1:+Ywpsq7O8HXn0nuIou7OrIPyXbp3wmkHB+jjWRnGsAI=
 github.com/chzyer/logex v1.2.1 h1:XHDu3E6q+gdHgsdTPH6ImJMIp436vR6MPtH8gP05QzM=
 github.com/chzyer/logex v1.2.1/go.mod h1:JLbx6lG2kDbNRFnfkgvh4eRJRPX1QCoOIWomwysCBrQ=
@@ -435,8 +443,8 @@ github.com/getsentry/sentry-go v0.20.0/go.mod h1:lc76E2QywIyW8WuBnwl8Lc4bkmQH4+w
 github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
 github.com/gin-contrib/sse v0.1.0 h1:Y/yl/+YNO8GZSjAhjMsSuLt29uWRFHdHYUb5lYOV9qE=
 github.com/gin-contrib/sse v0.1.0/go.mod h1:RHrZQHXnP2xjPF+u1gW/2HnVO7nvIa9PG3Gm+fLHvGI=
-github.com/gin-gonic/gin v1.8.1 h1:4+fr/el88TOO3ewCmQr8cx/CtZ/umlIRIs5M4NTNjf8=
-github.com/gin-gonic/gin v1.8.1/go.mod h1:ji8BvRH1azfM+SYow9zQ6SZMvR8qOMZHmsCuWR9tTTk=
+github.com/gin-gonic/gin v1.9.0 h1:OjyFBKICoexlu99ctXNR2gg+c5pKrKMuyjgARg9qeY8=
+github.com/gin-gonic/gin v1.9.0/go.mod h1:W1Me9+hsUSyj3CePGrd1/QrKJMSJ1Tu/0hFEH89961k=
 github.com/go-check/check v0.0.0-20180628173108-788fd7840127/go.mod h1:9ES+weclKsC9YodN5RgxqK/VD9HM9JsCSh7rNhMZE98=
 github.com/go-errors/errors v1.0.1/go.mod h1:f4zRHt4oKfwPJE5k8C9vpYG+aDHdBFUsgrm6/TyX73Q=
 github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
@@ -457,13 +465,13 @@ github.com/go-logfmt/logfmt v0.5.0/go.mod h1:wCYkCAKZfumFQihp8CzCvQ3paCTfi41vtzG
 github.com/go-logfmt/logfmt v0.6.0 h1:wGYYu3uicYdqXVgoYbvnkrPVXkuLM1p1ifugDMEdRi4=
 github.com/go-logfmt/logfmt v0.6.0/go.mod h1:WYhtIu8zTZfxdn5+rREduYbwxfcBr/Vr6KEVveWlfTs=
 github.com/go-martini/martini v0.0.0-20170121215854-22fa46961aab/go.mod h1:/P9AEU963A2AYjv4d1V5eVL1CQbEJq6aCNHDDjibzu8=
-github.com/go-playground/assert/v2 v2.0.1/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
-github.com/go-playground/locales v0.14.0 h1:u50s323jtVGugKlcYeyzC0etD1HifMjqmJqb8WugfUU=
-github.com/go-playground/locales v0.14.0/go.mod h1:sawfccIbzZTqEDETgFXqTho0QybSa7l++s0DH+LDiLs=
-github.com/go-playground/universal-translator v0.18.0 h1:82dyy6p4OuJq4/CByFNOn/jYrnRPArHwAcmLoJZxyho=
-github.com/go-playground/universal-translator v0.18.0/go.mod h1:UvRDBj+xPUEGrFYl+lu/H90nyDXpg0fqeB/AQUGNTVA=
-github.com/go-playground/validator/v10 v10.10.0/go.mod h1:74x4gJWsvQexRdW8Pn3dXSGrTK4nAUsbPlLADvpJkos=
-github.com/go-playground/validator/v10 v10.11.1 h1:prmOlTVv+YjZjmRmNSF3VmspqJIxJWXmqUsHwfTRRkQ=
+github.com/go-playground/assert/v2 v2.2.0/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
+github.com/go-playground/locales v0.14.1 h1:EWaQ/wswjilfKLTECiXz7Rh+3BjFhfDFKv/oXslEjJA=
+github.com/go-playground/locales v0.14.1/go.mod h1:hxrqLVvrK65+Rwrd5Fc6F2O76J/NuW9t0sjnWqG1slY=
+github.com/go-playground/universal-translator v0.18.1 h1:Bcnm0ZwsGyWbCzImXv+pAJnYK9S473LQFuzCbDbfSFY=
+github.com/go-playground/universal-translator v0.18.1/go.mod h1:xekY+UJKNuX9WP91TpwSH2VMlDf28Uj24BCp08ZFTUY=
+github.com/go-playground/validator/v10 v10.11.2 h1:q3SHpufmypg+erIExEKUmsgmhDTyhcJ38oeKGACXohU=
+github.com/go-playground/validator/v10 v10.11.2/go.mod h1:NieE624vt4SCTJtD87arVLvdmjPAeV8BQlHtMnw9D7s=
 github.com/go-sql-driver/mysql v1.4.0/go.mod h1:zAC/RDZ24gD3HViQzih4MyKcchzm+sOG5ZlKdlhCg5w=
 github.com/go-stack/stack v1.8.0/go.mod h1:v0f6uXyyMGvRgIKkXu+yp6POWl0qKG85gN/melR3HDY=
 github.com/go-task/slim-sprig v0.0.0-20210107165309-348f09dbbbc0/go.mod h1:fyg7847qk6SyHyPtNmDHnmrv/HOrqktSC+C9fM+CJOE=
@@ -473,8 +481,8 @@ github.com/gobwas/pool v0.2.0 h1:QEmUOlnSjWtnpRGHF3SauEiOsy82Cup83Vf2LcMlnc8=
 github.com/gobwas/pool v0.2.0/go.mod h1:q8bcK0KcYlCgd9e7WYLm9LpyS+YeLd8JVDW6WezmKEw=
 github.com/gobwas/ws v1.0.2 h1:CoAavW/wd/kulfZmSIBt6p24n4j7tHgNVCjsfHVNUbo=
 github.com/gobwas/ws v1.0.2/go.mod h1:szmBTxLgaFppYjEmNtny/v3w89xOydFnnZMcgRRu/EM=
-github.com/goccy/go-json v0.9.7/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
-github.com/goccy/go-json v0.9.11 h1:/pAaQDLHEoCq/5FFmSKBswWmK6H0e8g4159Kc/X/nqk=
+github.com/goccy/go-json v0.10.0 h1:mXKd9Qw4NuzShiRlOXKews24ufknHO7gx30lsDyokKA=
+github.com/goccy/go-json v0.10.0/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2 h1:ZpnhV/YsD2/4cESfV5+Hoeu/iUR3ruzNvZ+yQfO03a0=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2/go.mod h1:bBOAhwG1umN6/6ZUMtDFBMQR8jRg9O75tm9K00oMsK4=
 github.com/godbus/dbus/v5 v5.0.4/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
@@ -742,7 +750,10 @@ github.com/klauspost/compress v1.12.3/go.mod h1:8dP1Hq4DHOhN9w426knH3Rhby4rFm6D8
 github.com/klauspost/compress v1.15.11/go.mod h1:QPwzmACJjUTFsnSHH934V6woptycfrDDJnH7hvFVbGM=
 github.com/klauspost/compress v1.16.5 h1:IFV2oUNUzZaz+XyusxpLzpzS8Pt5rh0Z16For/djlyI=
 github.com/klauspost/compress v1.16.5/go.mod h1:ntbaceVETuRiXiv4DpjP66DpAtAGkEQskQzEyD//IeE=
+github.com/klauspost/cpuid v1.2.1 h1:vJi+O/nMdFt0vqm8NZBI6wzALWdA2X+egi0ogNyrC/w=
 github.com/klauspost/cpuid v1.2.1/go.mod h1:Pj4uuM528wm8OyEC2QMXAi2YiTZ96dNQPGgoMS4s3ek=
+github.com/klauspost/cpuid/v2 v2.0.9 h1:lgaqFMSdTdQYdZ04uHyN2d/eKdOMyi2YLSvlQIBFYa4=
+github.com/klauspost/cpuid/v2 v2.0.9/go.mod h1:FInQzS24/EEf25PyTYn52gqo7WaD8xa0213Md/qVLRg=
 github.com/konsorten/go-windows-terminal-sequences v1.0.1/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/konsorten/go-windows-terminal-sequences v1.0.3/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/kr/fs v0.1.0/go.mod h1:FFnZGqtBN9Gxj7eW1uZ42v5BccTP0vu6NEaFoC2HwRg=
@@ -789,6 +800,7 @@ github.com/mattn/go-isatty v0.0.9/go.mod h1:YNRxwqDuOph6SZLI9vUUz6OYw3QyUt7WiY2y
 github.com/mattn/go-isatty v0.0.12/go.mod h1:cbi8OIDigv2wuxKPP5vlRcQ1OAZbq2CE4Kysco4FUpU=
 github.com/mattn/go-isatty v0.0.14/go.mod h1:7GGIvUiUoEMVVmxf/4nioHXj79iQHKdU27kJ6hsGG94=
 github.com/mattn/go-isatty v0.0.16/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
+github.com/mattn/go-isatty v0.0.17/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
 github.com/mattn/go-isatty v0.0.18 h1:DOKFKCQ7FNG2L1rbrmstDN4QVRdS89Nkh85u68Uwp98=
 github.com/mattn/go-isatty v0.0.18/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
 github.com/mattn/go-runewidth v0.0.2/go.mod h1:LwmH8dsx7+W8Uxz3IHJYH5QSwggIsqBzpuz5H//U1FU=
@@ -881,7 +893,7 @@ github.com/pascaldekloe/goe v0.1.0 h1:cBOtyMzM9HTpWjXfbbunk26uA6nG3a8n06Wieeh0Mw
 github.com/pascaldekloe/goe v0.1.0/go.mod h1:lzWF7FIEvWOWxwDKqyGYQf6ZUaNfKdP144TG7ZOy1lc=
 github.com/pborman/uuid v1.2.0/go.mod h1:X/NO0urCmaxf9VXbdlT7C2Yzkj2IKimNn4k+gtPdI/k=
 github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
-github.com/pelletier/go-toml/v2 v2.0.1/go.mod h1:r9LEWfGN8R5k0VXJ+0BkIe7MYkRdwZOjgMj2KwnJFUo=
+github.com/pelletier/go-toml/v2 v2.0.6/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/pelletier/go-toml/v2 v2.0.7 h1:muncTPStnKRos5dpVKULv2FVd4bMOhNePj9CjgDb8Us=
 github.com/pelletier/go-toml/v2 v2.0.7/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/performancecopilot/speed v3.0.0+incompatible/go.mod h1:/CLtqpZ5gBg1M9iaPbIdPPGyKcA8hKdoy6hAWba7Yac=
@@ -1029,13 +1041,14 @@ github.com/tidwall/btree v1.6.0 h1:LDZfKfQIBHGHWSwckhXI0RPSXzlo+KYdjK7FWSqOzzg=
 github.com/tidwall/btree v1.6.0/go.mod h1:twD9XRA5jj9VUQGELzDO4HPQTNJsoWWfYEL+EUQ2cKY=
 github.com/tmc/grpc-websocket-proxy v0.0.0-20170815181823-89b8d40f7ca8/go.mod h1:ncp9v5uamzpCO7NfCPTXjqaC+bZgJeR0sMTm6dMHP7U=
 github.com/tv42/httpunix v0.0.0-20150427012821-b75d8614f926/go.mod h1:9ESjWnEqriFuLhtthL60Sar/7RFoluCcXsuvEwTV5KM=
+github.com/twitchyliquid64/golang-asm v0.15.1 h1:SU5vSMR7hnwNxj24w34ZyCi/FmDZTkS4MhqMhdFk5YI=
+github.com/twitchyliquid64/golang-asm v0.15.1/go.mod h1:a1lVb/DtPvCB8fslRZhAngC2+aY1QWCk3Cedj/Gdt08=
+github.com/ugorji/go v1.1.7 h1:/68gy2h+1mWMrwZFeD1kQialdSzAb432dtpeJ42ovdo=
 github.com/ugorji/go v1.1.7/go.mod h1:kZn38zHttfInRq0xu/PH0az30d+z6vm202qpg1oXVMw=
-github.com/ugorji/go v1.2.7 h1:qYhyWUUd6WbiM+C6JZAUkIJt/1WrjzNHY9+KCIjVqTo=
-github.com/ugorji/go v1.2.7/go.mod h1:nF9osbDWLy6bDVv/Rtoh6QgnvNDpmCalQV5urGCCS6M=
 github.com/ugorji/go/codec v0.0.0-20181204163529-d75b2dcb6bc8/go.mod h1:VFNgLljTbGfSG7qAOspJ7OScBnGdDN/yBr0sguwnwf0=
 github.com/ugorji/go/codec v1.1.7/go.mod h1:Ax+UKWsSmolVDwsd+7N3ZtXu+yMGCf907BLYF3GoBXY=
-github.com/ugorji/go/codec v1.2.7 h1:YPXUKf7fYbp/y8xloBqZOw2qaVggbfwMlI8WM3wZUJ0=
-github.com/ugorji/go/codec v1.2.7/go.mod h1:WGN1fab3R1fzQlVQTkfxVtIBhWDRqOviHU95kRgeqEY=
+github.com/ugorji/go/codec v1.2.9 h1:rmenucSohSTiyL09Y+l2OCk+FrMxGMzho2+tjr5ticU=
+github.com/ugorji/go/codec v1.2.9/go.mod h1:UNopzCgEMSXjBc6AOMqYvWC1ktqTAfzJZUZgYf6w6lg=
 github.com/ulikunitz/xz v0.5.10/go.mod h1:nbz6k7qbPmH4IRqmfOplQw/tblSgqTqBwxkY0oWt/14=
 github.com/ulikunitz/xz v0.5.11 h1:kpFauv27b6ynzBNT/Xy+1k+fK4WswhN/6PN5WhFAGw8=
 github.com/ulikunitz/xz v0.5.11/go.mod h1:nbz6k7qbPmH4IRqmfOplQw/tblSgqTqBwxkY0oWt/14=
@@ -1094,6 +1107,8 @@ go.uber.org/tools v0.0.0-20190618225709-2cfd321de3ee/go.mod h1:vJERXedbb3MVM5f9E
 go.uber.org/zap v1.10.0/go.mod h1:vwi/ZaCAaUcBkycHslxD9B2zi4UTXhF60s6SWpuDF0Q=
 go.uber.org/zap v1.13.0/go.mod h1:zwrFLgMcdUuIBviXEYEH1YKNaOBnKXsx2IPda5bBwHM=
 go.uber.org/zap v1.18.1/go.mod h1:xg/QME4nWcxGxrpdeYfq7UvYrLh66cuVKdrbD1XF/NI=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670 h1:18EFjUmQOcUvxNYSkA6jO9VAiXCnxFY6NyDX0bHDmkU=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670/go.mod h1:5om86z9Hs0C8fWVUuoMHwpExlXzs5Tkyp9hOrfG7pp8=
 golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181029021203-45a5f77698d3/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181203042331-505ab145d0a9/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
@@ -1108,9 +1123,9 @@ golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPh
 golang.org/x/crypto v0.0.0-20200728195943-123391ffb6de/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20210421170649-83a5a9bb288b/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
-golang.org/x/crypto v0.0.0-20210711020723-a769d52b0f97/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20210921155107-089bfa567519/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20211108221036-ceb1ce70b4fa/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
+golang.org/x/crypto v0.5.0/go.mod h1:NK/OQwhpMQP3MwtdjgLlYHnH9ebylxKWv3e0fK+mkQU=
 golang.org/x/crypto v0.9.0 h1:LF6fAI+IutBocDJ2OT0Q1g8plpYljMZ4+lty+dsqw3g=
 golang.org/x/crypto v0.9.0/go.mod h1:yrmDGqONDYtNj3tH8X9dzUun2m2lzPa9ngI6/RUPGR0=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
@@ -1216,6 +1231,8 @@ golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug
 golang.org/x/net v0.0.0-20220909164309-bea034e7d591/go.mod h1:YDH+HFinaLZZlnHAfSS6ZXJJ9M9t4Dl22yv3iI2vPwk=
 golang.org/x/net v0.0.0-20221014081412-f15817d10f9b/go.mod h1:YDH+HFinaLZZlnHAfSS6ZXJJ9M9t4Dl22yv3iI2vPwk=
 golang.org/x/net v0.1.0/go.mod h1:Cx3nUiGt4eDBEyega/BKRp+/AlGL8hYe7U9odMt2Cco=
+golang.org/x/net v0.5.0/go.mod h1:DivGGAXEgPSlEBzxGzZI+ZLohi+xUj054jfeKui00ws=
+golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
 golang.org/x/net v0.10.0 h1:X2//UzNDwYmtCLn7To6G58Wr6f5ahEAQgKNzv9Y951M=
 golang.org/x/net v0.10.0/go.mod h1:0qNGK6F8kojg2nk9dLZ2mShWaEBan6FAoqfSigmmuDg=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
@@ -1363,12 +1380,16 @@ golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20221010170243-090e33056c14/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.1.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.4.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.5.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.8.0 h1:EBmGv8NaZBZTWvrbjNoL6HVt+IVy3QDQpJs7VRIw3tU=
 golang.org/x/sys v0.8.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/term v0.1.0/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
+golang.org/x/term v0.4.0/go.mod h1:9P2UbLfCdcvo3p/nzKvsmas4TnlujnuoV9hGgYzW1lQ=
+golang.org/x/term v0.5.0/go.mod h1:jMB1sMXY+tzblOD4FWmEbocvup2/aLOaQEp7JmGp78k=
 golang.org/x/term v0.8.0 h1:n5xxQn2i3PC0yLAbjTpNT85q/Kgzcr2gIoX9OrJUols=
 golang.org/x/term v0.8.0/go.mod h1:xPskH00ivmX89bAKVGSKKtLOWNx2+17Eiy94tnKShWo=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1380,7 +1401,10 @@ golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
+golang.org/x/text v0.3.8/go.mod h1:E6s5w1FMmriuDzIBO73fBruAKo1PCIq6d2Q6DHfQ8WQ=
 golang.org/x/text v0.4.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.6.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/text v0.9.0 h1:2sjJmO8cDvYveuX97RDLsxlyUxLl+GHoLxBiRdHllBE=
 golang.org/x/text v0.9.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -1747,6 +1771,7 @@ nhooyr.io/websocket v1.8.6/go.mod h1:B70DZP8IakI65RVQ51MsWP/8jndNma26DVA/nFSCgW0
 pgregory.net/rapid v0.5.7 h1:p7/XbOgyFY1I/3Q12UTXfos70VZTcgc3WeoyiEru5cs=
 pgregory.net/rapid v0.5.7/go.mod h1:PY5XlDGj0+V1FCq0o192FdRhpKHGTRIWBgqjDBTrq04=
 rsc.io/binaryregexp v0.2.0/go.mod h1:qTv7/COck+e2FymRvadv62gMdZztPaShugOCi3I+8D8=
+rsc.io/pdf v0.1.1/go.mod h1:n8OzWcQ6Sp37PL01nO98y4iUCRdTGarVfzxY20ICaU4=
 rsc.io/quote/v3 v3.1.0/go.mod h1:yEA65RcK8LyAZtP9Kv3t0HmxON59tX3rD+tICJqUlj0=
 rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
 sigs.k8s.io/yaml v1.1.0/go.mod h1:UJmg0vDUVViEyp3mgSv9WPwZCDxu4rQW1olrI1uml+o=
```

### tools/confix/go.mod
```diff
@@ -157,7 +157,7 @@ require (
 
 replace cosmossdk.io/collections => ../../collections
 
-// Fix upstream GHSA-h395-qcrw-5vmq vulnerability.
+// Fix upstream GHSA-h395-qcrw-5vmq and GHSA-3vp4-m3rf-835h vulnerabilities.
 // TODO Remove it: https://github.com/cosmos/cosmos-sdk/issues/10409
 // TODO investigate if we can outright delete this dependency, otherwise go install won't work :(
-replace github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.8.1
+replace github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.9.0
```

### tools/confix/go.sum
```diff
@@ -117,6 +117,9 @@ github.com/btcsuite/btcd/btcec/v2 v2.3.2/go.mod h1:zYzJ8etWJQIv1Ogk7OzpWjowwOdXY
 github.com/btcsuite/btcd/btcutil v1.1.2 h1:XLMbX8JQEiwMcYft2EGi8zPUkoa0abKIU6/BJSRsjzQ=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1 h1:q0rUy8C/TYNBQS1+CGKw68tLOFYSNEs0TFnxxnS9+4U=
 github.com/bufbuild/protocompile v0.4.0 h1:LbFKd2XowZvQ/kajzguUp2DC9UEIQhIq77fZZlaQsNA=
+github.com/bytedance/sonic v1.5.0/go.mod h1:ED5hyg4y6t3/9Ku1R6dU/4KyJ48DZ4jPhfY1O2AihPM=
+github.com/bytedance/sonic v1.8.0 h1:ea0Xadu+sHlu7x5O3gKhRpQ1IKiMrSiHttPF0ybECuA=
+github.com/bytedance/sonic v1.8.0/go.mod h1:i736AoUSYt75HyZLoJW9ERYxcy6eaN6h4BZXU064P/U=
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
 github.com/cenkalti/backoff v2.2.1+incompatible h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=
 github.com/cenkalti/backoff v2.2.1+incompatible/go.mod h1:90ReRw6GdpyfrHakVjL/QHaoyV4aDUVVkXQJJJ3NXXM=
@@ -129,6 +132,9 @@ github.com/cespare/xxhash v1.1.0/go.mod h1:XrSqR1VqqWfGrhpAt58auRo0WTKS1nRRg3ghf
 github.com/cespare/xxhash/v2 v2.1.1/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/cespare/xxhash/v2 v2.2.0 h1:DC2CZ1Ep5Y4k3ZQ899DldepgrayRUGE6BBZ/cd9Cj44=
 github.com/cespare/xxhash/v2 v2.2.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
+github.com/chenzhuoyu/base64x v0.0.0-20211019084208-fb5309c8db06/go.mod h1:DH46F32mSOjUmXrMHnKwZdA8wcEefY7UVqBKYGjpdQY=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311 h1:qSGYFH7+jGhDF8vLC+iwCD4WpbV1EBDSzWkJODFLams=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311/go.mod h1:b583jCggY9gE99b6G5LEC39OIiVsWj+R97kbl5odCEk=
 github.com/chzyer/logex v1.1.10/go.mod h1:+Ywpsq7O8HXn0nuIou7OrIPyXbp3wmkHB+jjWRnGsAI=
 github.com/chzyer/readline v0.0.0-20180603132655-2972be24d48e/go.mod h1:nSuG5e5PlCu98SY8svDHJxuZscDgtXS6KTTbou5AhLI=
 github.com/chzyer/readline v1.5.1 h1:upd/6fQk4src78LMRzh5vItIt361/o4uq553V8B5sGI=
@@ -279,8 +285,8 @@ github.com/getsentry/sentry-go v0.20.0/go.mod h1:lc76E2QywIyW8WuBnwl8Lc4bkmQH4+w
 github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
 github.com/gin-contrib/sse v0.1.0 h1:Y/yl/+YNO8GZSjAhjMsSuLt29uWRFHdHYUb5lYOV9qE=
 github.com/gin-contrib/sse v0.1.0/go.mod h1:RHrZQHXnP2xjPF+u1gW/2HnVO7nvIa9PG3Gm+fLHvGI=
-github.com/gin-gonic/gin v1.8.1 h1:4+fr/el88TOO3ewCmQr8cx/CtZ/umlIRIs5M4NTNjf8=
-github.com/gin-gonic/gin v1.8.1/go.mod h1:ji8BvRH1azfM+SYow9zQ6SZMvR8qOMZHmsCuWR9tTTk=
+github.com/gin-gonic/gin v1.9.0 h1:OjyFBKICoexlu99ctXNR2gg+c5pKrKMuyjgARg9qeY8=
+github.com/gin-gonic/gin v1.9.0/go.mod h1:W1Me9+hsUSyj3CePGrd1/QrKJMSJ1Tu/0hFEH89961k=
 github.com/go-check/check v0.0.0-20180628173108-788fd7840127/go.mod h1:9ES+weclKsC9YodN5RgxqK/VD9HM9JsCSh7rNhMZE98=
 github.com/go-errors/errors v1.0.1/go.mod h1:f4zRHt4oKfwPJE5k8C9vpYG+aDHdBFUsgrm6/TyX73Q=
 github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
@@ -301,13 +307,13 @@ github.com/go-logfmt/logfmt v0.5.0/go.mod h1:wCYkCAKZfumFQihp8CzCvQ3paCTfi41vtzG
 github.com/go-logfmt/logfmt v0.6.0 h1:wGYYu3uicYdqXVgoYbvnkrPVXkuLM1p1ifugDMEdRi4=
 github.com/go-logfmt/logfmt v0.6.0/go.mod h1:WYhtIu8zTZfxdn5+rREduYbwxfcBr/Vr6KEVveWlfTs=
 github.com/go-martini/martini v0.0.0-20170121215854-22fa46961aab/go.mod h1:/P9AEU963A2AYjv4d1V5eVL1CQbEJq6aCNHDDjibzu8=
-github.com/go-playground/assert/v2 v2.0.1/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
-github.com/go-playground/locales v0.14.0 h1:u50s323jtVGugKlcYeyzC0etD1HifMjqmJqb8WugfUU=
-github.com/go-playground/locales v0.14.0/go.mod h1:sawfccIbzZTqEDETgFXqTho0QybSa7l++s0DH+LDiLs=
-github.com/go-playground/universal-translator v0.18.0 h1:82dyy6p4OuJq4/CByFNOn/jYrnRPArHwAcmLoJZxyho=
-github.com/go-playground/universal-translator v0.18.0/go.mod h1:UvRDBj+xPUEGrFYl+lu/H90nyDXpg0fqeB/AQUGNTVA=
-github.com/go-playground/validator/v10 v10.10.0/go.mod h1:74x4gJWsvQexRdW8Pn3dXSGrTK4nAUsbPlLADvpJkos=
-github.com/go-playground/validator/v10 v10.11.1 h1:prmOlTVv+YjZjmRmNSF3VmspqJIxJWXmqUsHwfTRRkQ=
+github.com/go-playground/assert/v2 v2.2.0/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
+github.com/go-playground/locales v0.14.1 h1:EWaQ/wswjilfKLTECiXz7Rh+3BjFhfDFKv/oXslEjJA=
+github.com/go-playground/locales v0.14.1/go.mod h1:hxrqLVvrK65+Rwrd5Fc6F2O76J/NuW9t0sjnWqG1slY=
+github.com/go-playground/universal-translator v0.18.1 h1:Bcnm0ZwsGyWbCzImXv+pAJnYK9S473LQFuzCbDbfSFY=
+github.com/go-playground/universal-translator v0.18.1/go.mod h1:xekY+UJKNuX9WP91TpwSH2VMlDf28Uj24BCp08ZFTUY=
+github.com/go-playground/validator/v10 v10.11.2 h1:q3SHpufmypg+erIExEKUmsgmhDTyhcJ38oeKGACXohU=
+github.com/go-playground/validator/v10 v10.11.2/go.mod h1:NieE624vt4SCTJtD87arVLvdmjPAeV8BQlHtMnw9D7s=
 github.com/go-sql-driver/mysql v1.4.0/go.mod h1:zAC/RDZ24gD3HViQzih4MyKcchzm+sOG5ZlKdlhCg5w=
 github.com/go-stack/stack v1.8.0/go.mod h1:v0f6uXyyMGvRgIKkXu+yp6POWl0qKG85gN/melR3HDY=
 github.com/go-task/slim-sprig v0.0.0-20210107165309-348f09dbbbc0/go.mod h1:fyg7847qk6SyHyPtNmDHnmrv/HOrqktSC+C9fM+CJOE=
@@ -317,8 +323,8 @@ github.com/gobwas/pool v0.2.0 h1:QEmUOlnSjWtnpRGHF3SauEiOsy82Cup83Vf2LcMlnc8=
 github.com/gobwas/pool v0.2.0/go.mod h1:q8bcK0KcYlCgd9e7WYLm9LpyS+YeLd8JVDW6WezmKEw=
 github.com/gobwas/ws v1.0.2 h1:CoAavW/wd/kulfZmSIBt6p24n4j7tHgNVCjsfHVNUbo=
 github.com/gobwas/ws v1.0.2/go.mod h1:szmBTxLgaFppYjEmNtny/v3w89xOydFnnZMcgRRu/EM=
-github.com/goccy/go-json v0.9.7/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
-github.com/goccy/go-json v0.9.11 h1:/pAaQDLHEoCq/5FFmSKBswWmK6H0e8g4159Kc/X/nqk=
+github.com/goccy/go-json v0.10.0 h1:mXKd9Qw4NuzShiRlOXKews24ufknHO7gx30lsDyokKA=
+github.com/goccy/go-json v0.10.0/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2 h1:ZpnhV/YsD2/4cESfV5+Hoeu/iUR3ruzNvZ+yQfO03a0=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2/go.mod h1:bBOAhwG1umN6/6ZUMtDFBMQR8jRg9O75tm9K00oMsK4=
 github.com/godbus/dbus/v5 v5.0.4/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
@@ -541,7 +547,10 @@ github.com/klauspost/compress v1.11.7/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYs
 github.com/klauspost/compress v1.12.3/go.mod h1:8dP1Hq4DHOhN9w426knH3Rhby4rFm6D8eO+e+Dq5Gzg=
 github.com/klauspost/compress v1.16.5 h1:IFV2oUNUzZaz+XyusxpLzpzS8Pt5rh0Z16For/djlyI=
 github.com/klauspost/compress v1.16.5/go.mod h1:ntbaceVETuRiXiv4DpjP66DpAtAGkEQskQzEyD//IeE=
+github.com/klauspost/cpuid v1.2.1 h1:vJi+O/nMdFt0vqm8NZBI6wzALWdA2X+egi0ogNyrC/w=
 github.com/klauspost/cpuid v1.2.1/go.mod h1:Pj4uuM528wm8OyEC2QMXAi2YiTZ96dNQPGgoMS4s3ek=
+github.com/klauspost/cpuid/v2 v2.0.9 h1:lgaqFMSdTdQYdZ04uHyN2d/eKdOMyi2YLSvlQIBFYa4=
+github.com/klauspost/cpuid/v2 v2.0.9/go.mod h1:FInQzS24/EEf25PyTYn52gqo7WaD8xa0213Md/qVLRg=
 github.com/konsorten/go-windows-terminal-sequences v1.0.1/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/konsorten/go-windows-terminal-sequences v1.0.3/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/kr/fs v0.1.0/go.mod h1:FFnZGqtBN9Gxj7eW1uZ42v5BccTP0vu6NEaFoC2HwRg=
@@ -587,6 +596,7 @@ github.com/mattn/go-isatty v0.0.9/go.mod h1:YNRxwqDuOph6SZLI9vUUz6OYw3QyUt7WiY2y
 github.com/mattn/go-isatty v0.0.12/go.mod h1:cbi8OIDigv2wuxKPP5vlRcQ1OAZbq2CE4Kysco4FUpU=
 github.com/mattn/go-isatty v0.0.14/go.mod h1:7GGIvUiUoEMVVmxf/4nioHXj79iQHKdU27kJ6hsGG94=
 github.com/mattn/go-isatty v0.0.16/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
+github.com/mattn/go-isatty v0.0.17/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
 github.com/mattn/go-isatty v0.0.18 h1:DOKFKCQ7FNG2L1rbrmstDN4QVRdS89Nkh85u68Uwp98=
 github.com/mattn/go-isatty v0.0.18/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
 github.com/mattn/go-runewidth v0.0.2/go.mod h1:LwmH8dsx7+W8Uxz3IHJYH5QSwggIsqBzpuz5H//U1FU=
@@ -677,7 +687,7 @@ github.com/pascaldekloe/goe v0.1.0 h1:cBOtyMzM9HTpWjXfbbunk26uA6nG3a8n06Wieeh0Mw
 github.com/pascaldekloe/goe v0.1.0/go.mod h1:lzWF7FIEvWOWxwDKqyGYQf6ZUaNfKdP144TG7ZOy1lc=
 github.com/pborman/uuid v1.2.0/go.mod h1:X/NO0urCmaxf9VXbdlT7C2Yzkj2IKimNn4k+gtPdI/k=
 github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
-github.com/pelletier/go-toml/v2 v2.0.1/go.mod h1:r9LEWfGN8R5k0VXJ+0BkIe7MYkRdwZOjgMj2KwnJFUo=
+github.com/pelletier/go-toml/v2 v2.0.6/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/pelletier/go-toml/v2 v2.0.7 h1:muncTPStnKRos5dpVKULv2FVd4bMOhNePj9CjgDb8Us=
 github.com/pelletier/go-toml/v2 v2.0.7/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/performancecopilot/speed v3.0.0+incompatible/go.mod h1:/CLtqpZ5gBg1M9iaPbIdPPGyKcA8hKdoy6hAWba7Yac=
@@ -825,13 +835,14 @@ github.com/tidwall/btree v1.6.0 h1:LDZfKfQIBHGHWSwckhXI0RPSXzlo+KYdjK7FWSqOzzg=
 github.com/tidwall/btree v1.6.0/go.mod h1:twD9XRA5jj9VUQGELzDO4HPQTNJsoWWfYEL+EUQ2cKY=
 github.com/tmc/grpc-websocket-proxy v0.0.0-20170815181823-89b8d40f7ca8/go.mod h1:ncp9v5uamzpCO7NfCPTXjqaC+bZgJeR0sMTm6dMHP7U=
 github.com/tv42/httpunix v0.0.0-20150427012821-b75d8614f926/go.mod h1:9ESjWnEqriFuLhtthL60Sar/7RFoluCcXsuvEwTV5KM=
+github.com/twitchyliquid64/golang-asm v0.15.1 h1:SU5vSMR7hnwNxj24w34ZyCi/FmDZTkS4MhqMhdFk5YI=
+github.com/twitchyliquid64/golang-asm v0.15.1/go.mod h1:a1lVb/DtPvCB8fslRZhAngC2+aY1QWCk3Cedj/Gdt08=
+github.com/ugorji/go v1.1.7 h1:/68gy2h+1mWMrwZFeD1kQialdSzAb432dtpeJ42ovdo=
 github.com/ugorji/go v1.1.7/go.mod h1:kZn38zHttfInRq0xu/PH0az30d+z6vm202qpg1oXVMw=
-github.com/ugorji/go v1.2.7 h1:qYhyWUUd6WbiM+C6JZAUkIJt/1WrjzNHY9+KCIjVqTo=
-github.com/ugorji/go v1.2.7/go.mod h1:nF9osbDWLy6bDVv/Rtoh6QgnvNDpmCalQV5urGCCS6M=
 github.com/ugorji/go/codec v0.0.0-20181204163529-d75b2dcb6bc8/go.mod h1:VFNgLljTbGfSG7qAOspJ7OScBnGdDN/yBr0sguwnwf0=
 github.com/ugorji/go/codec v1.1.7/go.mod h1:Ax+UKWsSmolVDwsd+7N3ZtXu+yMGCf907BLYF3GoBXY=
-github.com/ugorji/go/codec v1.2.7 h1:YPXUKf7fYbp/y8xloBqZOw2qaVggbfwMlI8WM3wZUJ0=
-github.com/ugorji/go/codec v1.2.7/go.mod h1:WGN1fab3R1fzQlVQTkfxVtIBhWDRqOviHU95kRgeqEY=
+github.com/ugorji/go/codec v1.2.9 h1:rmenucSohSTiyL09Y+l2OCk+FrMxGMzho2+tjr5ticU=
+github.com/ugorji/go/codec v1.2.9/go.mod h1:UNopzCgEMSXjBc6AOMqYvWC1ktqTAfzJZUZgYf6w6lg=
 github.com/urfave/cli v1.20.0/go.mod h1:70zkFmudgCuE/ngEzBv17Jvp/497gISqfk5gWijbERA=
 github.com/urfave/cli v1.22.1/go.mod h1:Gos4lmkARVdJ6EkW0WaNv/tZAAMe9V7XWyB60NtXRu0=
 github.com/urfave/negroni v1.0.0/go.mod h1:Meg73S6kFm/4PpbYdq35yYWoCZ9mS/YSx+lKnmiohz4=
@@ -854,6 +865,7 @@ github.com/yuin/goldmark v1.1.27/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9de
 github.com/yuin/goldmark v1.1.32/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.2.1/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.3.5/go.mod h1:mwnBkeHKe2W/ZEtQ+71ViKU8L12m81fl3OWwC1Zlc8k=
+github.com/yuin/goldmark v1.4.13/go.mod h1:6yULJ656Px+3vBD8DxQVa3kxgyrAnzto9xy5taEt/CY=
 github.com/zondax/hid v0.9.1 h1:gQe66rtmyZ8VeGFcOpbuH3r7erYtNEAezCAYu8LdkJo=
 github.com/zondax/hid v0.9.1/go.mod h1:l5wttcP0jwtdLjqjMMWFVEE7d1zO0jvSPA9OPZxWpEM=
 github.com/zondax/ledger-go v0.14.1 h1:Pip65OOl4iJ84WTpA4BKChvOufMhhbxED3BaihoZN4c=
@@ -883,6 +895,8 @@ go.uber.org/tools v0.0.0-20190618225709-2cfd321de3ee/go.mod h1:vJERXedbb3MVM5f9E
 go.uber.org/zap v1.10.0/go.mod h1:vwi/ZaCAaUcBkycHslxD9B2zi4UTXhF60s6SWpuDF0Q=
 go.uber.org/zap v1.13.0/go.mod h1:zwrFLgMcdUuIBviXEYEH1YKNaOBnKXsx2IPda5bBwHM=
 go.uber.org/zap v1.18.1/go.mod h1:xg/QME4nWcxGxrpdeYfq7UvYrLh66cuVKdrbD1XF/NI=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670 h1:18EFjUmQOcUvxNYSkA6jO9VAiXCnxFY6NyDX0bHDmkU=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670/go.mod h1:5om86z9Hs0C8fWVUuoMHwpExlXzs5Tkyp9hOrfG7pp8=
 golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181029021203-45a5f77698d3/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181203042331-505ab145d0a9/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
@@ -897,9 +911,9 @@ golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPh
 golang.org/x/crypto v0.0.0-20200728195943-123391ffb6de/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20210421170649-83a5a9bb288b/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
-golang.org/x/crypto v0.0.0-20210711020723-a769d52b0f97/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20210921155107-089bfa567519/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20211108221036-ceb1ce70b4fa/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
+golang.org/x/crypto v0.5.0/go.mod h1:NK/OQwhpMQP3MwtdjgLlYHnH9ebylxKWv3e0fK+mkQU=
 golang.org/x/crypto v0.9.0 h1:LF6fAI+IutBocDJ2OT0Q1g8plpYljMZ4+lty+dsqw3g=
 golang.org/x/crypto v0.9.0/go.mod h1:yrmDGqONDYtNj3tH8X9dzUun2m2lzPa9ngI6/RUPGR0=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
@@ -940,6 +954,7 @@ golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.2/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
+golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4/go.mod h1:jJ57K6gSWd91VN4djpZkiMVwK6gcyfeH4XE8wZrZaV4=
 golang.org/x/mod v0.8.0 h1:LUYupSeNrTNCGzR/hVBk2NHZO4hXcVaW1k4Qx7rjPx8=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -990,6 +1005,9 @@ golang.org/x/net v0.0.0-20210805182204-aaa1db679c0d/go.mod h1:9nx3DQGgdP8bBQD5qx
 golang.org/x/net v0.0.0-20211008194852-3b03d305991f/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
+golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
+golang.org/x/net v0.5.0/go.mod h1:DivGGAXEgPSlEBzxGzZI+ZLohi+xUj054jfeKui00ws=
+golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
 golang.org/x/net v0.10.0 h1:X2//UzNDwYmtCLn7To6G58Wr6f5ahEAQgKNzv9Y951M=
 golang.org/x/net v0.10.0/go.mod h1:0qNGK6F8kojg2nk9dLZ2mShWaEBan6FAoqfSigmmuDg=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
@@ -1012,6 +1030,7 @@ golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
+golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.2.0 h1:PUR+T4wwASmuSTYdKjYHI5TD22Wy5ogLU5qZCOLxBrI=
 golang.org/x/sync v0.2.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -1079,7 +1098,6 @@ golang.org/x/sys v0.0.0-20210423185535-09eb48e85fd7/go.mod h1:h1NjWce9XRLGQEsW7w
 golang.org/x/sys v0.0.0-20210510120138-977fb7262007/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210615035016-665e8c7367d1/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210630005230-0f9fa26af87c/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20210806184541-e5e7981a1069/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210809222454-d867a43fc93e/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210819135213-f52c844e1c1c/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210927094055-39ccf1dd6fa6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
@@ -1091,14 +1109,19 @@ golang.org/x/sys v0.0.0-20220315194320-039c03cc5b86/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220503163025-988cb79eb6c6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.0.0-20220722155257-8c9f86f7a55f/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20221010170243-090e33056c14/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.4.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.5.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.8.0 h1:EBmGv8NaZBZTWvrbjNoL6HVt+IVy3QDQpJs7VRIw3tU=
 golang.org/x/sys v0.8.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
+golang.org/x/term v0.4.0/go.mod h1:9P2UbLfCdcvo3p/nzKvsmas4TnlujnuoV9hGgYzW1lQ=
+golang.org/x/term v0.5.0/go.mod h1:jMB1sMXY+tzblOD4FWmEbocvup2/aLOaQEp7JmGp78k=
 golang.org/x/term v0.8.0 h1:n5xxQn2i3PC0yLAbjTpNT85q/Kgzcr2gIoX9OrJUols=
 golang.org/x/term v0.8.0/go.mod h1:xPskH00ivmX89bAKVGSKKtLOWNx2+17Eiy94tnKShWo=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1110,6 +1133,9 @@ golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
+golang.org/x/text v0.3.8/go.mod h1:E6s5w1FMmriuDzIBO73fBruAKo1PCIq6d2Q6DHfQ8WQ=
+golang.org/x/text v0.6.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/text v0.9.0 h1:2sjJmO8cDvYveuX97RDLsxlyUxLl+GHoLxBiRdHllBE=
 golang.org/x/text v0.9.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -1179,6 +1205,7 @@ golang.org/x/tools v0.0.0-20210108195828-e2f9c7f1fc8e/go.mod h1:emZCQorbCU4vsT4f
 golang.org/x/tools v0.1.0/go.mod h1:xkSsbof2nBLbhDlRMhhhyNLN/zl3eTqcnHD5viDpcZ0=
 golang.org/x/tools v0.1.1/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.3/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
+golang.org/x/tools v0.1.12/go.mod h1:hNGJHUnrk76NpqgfD5Aqm5Crs+Hm0VOH/i9J2+nxYbc=
 golang.org/x/tools v0.6.0 h1:BOw41kyTf3PuCW1pVQf8+Cyg8pMlkYB1oo9iJ6D/lKM=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
@@ -1302,7 +1329,6 @@ google.golang.org/protobuf v1.25.0/go.mod h1:9JNX74DMeImyA3h4bdi1ymwjUzf21/xIlba
 google.golang.org/protobuf v1.26.0-rc.1/go.mod h1:jlhhOSvTdKEhbULTjvd4ARK9grFBp09yW+WbY/TyQbw=
 google.golang.org/protobuf v1.26.0/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
 google.golang.org/protobuf v1.27.1/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
-google.golang.org/protobuf v1.28.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 google.golang.org/protobuf v1.28.1/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 google.golang.org/protobuf v1.30.0 h1:kPPoIgf3TsEvrm0PFe15JQ+570QVxYzEvvHqChK+cng=
 google.golang.org/protobuf v1.30.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
@@ -1355,6 +1381,7 @@ nhooyr.io/websocket v1.8.6/go.mod h1:B70DZP8IakI65RVQ51MsWP/8jndNma26DVA/nFSCgW0
 pgregory.net/rapid v0.5.7 h1:p7/XbOgyFY1I/3Q12UTXfos70VZTcgc3WeoyiEru5cs=
 pgregory.net/rapid v0.5.7/go.mod h1:PY5XlDGj0+V1FCq0o192FdRhpKHGTRIWBgqjDBTrq04=
 rsc.io/binaryregexp v0.2.0/go.mod h1:qTv7/COck+e2FymRvadv62gMdZztPaShugOCi3I+8D8=
+rsc.io/pdf v0.1.1/go.mod h1:n8OzWcQ6Sp37PL01nO98y4iUCRdTGarVfzxY20ICaU4=
 rsc.io/quote/v3 v3.1.0/go.mod h1:yEA65RcK8LyAZtP9Kv3t0HmxON59tX3rD+tICJqUlj0=
 rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
 sigs.k8s.io/yaml v1.1.0/go.mod h1:UJmg0vDUVViEyp3mgSv9WPwZCDxu4rQW1olrI1uml+o=
```

### tools/rosetta/go.mod
```diff
@@ -19,7 +19,7 @@ require (
 require (
 	cosmossdk.io/api v0.4.1 // indirect
 	cosmossdk.io/collections v0.1.0 // indirect
-	cosmossdk.io/core v0.6.1 // indirect
+	cosmossdk.io/core v0.7.0 // indirect
 	cosmossdk.io/depinject v1.0.0-alpha.3 // indirect
 	cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4 // indirect
 	cosmossdk.io/store v0.1.0-alpha.1.0.20230328185921-37ba88872dbc // indirect
@@ -142,7 +142,6 @@ require (
 // TODO: remove after merge of https://github.com/cosmos/cosmos-sdk/pull/15873 and tagging releases
 replace (
 	cosmossdk.io/collections => ../../collections // TODO: remove me after collections v0.2.0 is released
-	cosmossdk.io/core => ../../core
 	cosmossdk.io/store => ../../store
 	cosmossdk.io/x/tx => ../../x/tx
 	github.com/cosmos/cosmos-sdk => ../..
```

### tools/rosetta/go.sum
```diff
@@ -37,6 +37,8 @@ cloud.google.com/go/storage v1.10.0/go.mod h1:FLPqc6j+Ki4BU591ie1oL6qBQGu2Bl/tZ9
 cloud.google.com/go/storage v1.14.0/go.mod h1:GrKmX003DSIwi9o29oFT7YDnHYwZoctc3fOKtUw0Xmo=
 cosmossdk.io/api v0.4.1 h1:0ikaYM6GyxTYYcfBiyR8YnLCfhNnhKpEFnaSepCTmqg=
 cosmossdk.io/api v0.4.1/go.mod h1:jR7k5ok90LxW2lFUXvd8Vpo/dr4PpiyVegxdm7b1ZdE=
+cosmossdk.io/core v0.7.0 h1:GFss3qt2P9p23Cz24NnqLkslzb8n+B75A24x1JgJJp0=
+cosmossdk.io/core v0.7.0/go.mod h1:36hP0ZH/8ipsjzfcp0yKU4bqQXUGhS0/m1krWFCtwCc=
 cosmossdk.io/depinject v1.0.0-alpha.3 h1:6evFIgj//Y3w09bqOUOzEpFj5tsxBqdc5CfkO7z+zfw=
 cosmossdk.io/depinject v1.0.0-alpha.3/go.mod h1:eRbcdQ7MRpIPEM5YUJh8k97nxHpYbc3sMUnEtt8HPWU=
 cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4 h1:rOy7iw7HlwKc5Af5qIHLXdBx/F98o6du/I/WGwOW6eA=
```

### x/evidence/go.mod
```diff
@@ -4,7 +4,7 @@ go 1.20
 
 require (
 	cosmossdk.io/api v0.4.1
-	cosmossdk.io/core v0.6.1
+	cosmossdk.io/core v0.7.0
 	cosmossdk.io/depinject v1.0.0-alpha.3
 	cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4
 	cosmossdk.io/log v1.1.0
@@ -154,16 +154,15 @@ require (
 	sigs.k8s.io/yaml v1.3.0 // indirect
 )
 
-// Below are the long-lived replace of the Cosmos SDK
-// Fix upstream GHSA-h395-qcrw-5vmq vulnerability.
-// TODO Remove it: https://github.com/cosmos/cosmos-sdk/issues/10409
-replace github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.8.1
-
+// Below are the short-lived replace of the evidence module
 replace (
 	// TODO: remove me when collections v0.2.0 is released
 	cosmossdk.io/collections => ../../collections
-	cosmossdk.io/core => ../../core
 	cosmossdk.io/store => ../../store
 	cosmossdk.io/x/tx => ../tx
 	github.com/cosmos/cosmos-sdk => ../../
 )
+
+// Fix upstream GHSA-h395-qcrw-5vmq and GHSA-3vp4-m3rf-835h vulnerabilities.
+// TODO Remove it: https://github.com/cosmos/cosmos-sdk/issues/10409
+replace github.com/gin-gonic/gin => github.com/gin-gonic/gin v1.9.0
```

### x/evidence/go.sum
```diff
@@ -37,6 +37,8 @@ cloud.google.com/go/storage v1.10.0/go.mod h1:FLPqc6j+Ki4BU591ie1oL6qBQGu2Bl/tZ9
 cloud.google.com/go/storage v1.14.0/go.mod h1:GrKmX003DSIwi9o29oFT7YDnHYwZoctc3fOKtUw0Xmo=
 cosmossdk.io/api v0.4.1 h1:0ikaYM6GyxTYYcfBiyR8YnLCfhNnhKpEFnaSepCTmqg=
 cosmossdk.io/api v0.4.1/go.mod h1:jR7k5ok90LxW2lFUXvd8Vpo/dr4PpiyVegxdm7b1ZdE=
+cosmossdk.io/core v0.7.0 h1:GFss3qt2P9p23Cz24NnqLkslzb8n+B75A24x1JgJJp0=
+cosmossdk.io/core v0.7.0/go.mod h1:36hP0ZH/8ipsjzfcp0yKU4bqQXUGhS0/m1krWFCtwCc=
 cosmossdk.io/depinject v1.0.0-alpha.3 h1:6evFIgj//Y3w09bqOUOzEpFj5tsxBqdc5CfkO7z+zfw=
 cosmossdk.io/depinject v1.0.0-alpha.3/go.mod h1:eRbcdQ7MRpIPEM5YUJh8k97nxHpYbc3sMUnEtt8HPWU=
 cosmossdk.io/errors v1.0.0-beta.7.0.20230429155654-3ee8242364e4 h1:rOy7iw7HlwKc5Af5qIHLXdBx/F98o6du/I/WGwOW6eA=
@@ -112,6 +114,9 @@ github.com/btcsuite/btcd/btcec/v2 v2.3.2/go.mod h1:zYzJ8etWJQIv1Ogk7OzpWjowwOdXY
 github.com/btcsuite/btcd/btcutil v1.1.2 h1:XLMbX8JQEiwMcYft2EGi8zPUkoa0abKIU6/BJSRsjzQ=
 github.com/btcsuite/btcd/chaincfg/chainhash v1.0.1 h1:q0rUy8C/TYNBQS1+CGKw68tLOFYSNEs0TFnxxnS9+4U=
 github.com/bufbuild/protocompile v0.4.0 h1:LbFKd2XowZvQ/kajzguUp2DC9UEIQhIq77fZZlaQsNA=
+github.com/bytedance/sonic v1.5.0/go.mod h1:ED5hyg4y6t3/9Ku1R6dU/4KyJ48DZ4jPhfY1O2AihPM=
+github.com/bytedance/sonic v1.8.0 h1:ea0Xadu+sHlu7x5O3gKhRpQ1IKiMrSiHttPF0ybECuA=
+github.com/bytedance/sonic v1.8.0/go.mod h1:i736AoUSYt75HyZLoJW9ERYxcy6eaN6h4BZXU064P/U=
 github.com/casbin/casbin/v2 v2.1.2/go.mod h1:YcPU1XXisHhLzuxH9coDNf2FbKpjGlbCg3n9yuLkIJQ=
 github.com/cenkalti/backoff v2.2.1+incompatible h1:tNowT99t7UNflLxfYYSlKYsBpXdEet03Pg2g16Swow4=
 github.com/cenkalti/backoff v2.2.1+incompatible/go.mod h1:90ReRw6GdpyfrHakVjL/QHaoyV4aDUVVkXQJJJ3NXXM=
@@ -124,6 +129,9 @@ github.com/cespare/xxhash v1.1.0/go.mod h1:XrSqR1VqqWfGrhpAt58auRo0WTKS1nRRg3ghf
 github.com/cespare/xxhash/v2 v2.1.1/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
 github.com/cespare/xxhash/v2 v2.2.0 h1:DC2CZ1Ep5Y4k3ZQ899DldepgrayRUGE6BBZ/cd9Cj44=
 github.com/cespare/xxhash/v2 v2.2.0/go.mod h1:VGX0DQ3Q6kWi7AoAeZDth3/j3BFtOZR5XLFGgcrjCOs=
+github.com/chenzhuoyu/base64x v0.0.0-20211019084208-fb5309c8db06/go.mod h1:DH46F32mSOjUmXrMHnKwZdA8wcEefY7UVqBKYGjpdQY=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311 h1:qSGYFH7+jGhDF8vLC+iwCD4WpbV1EBDSzWkJODFLams=
+github.com/chenzhuoyu/base64x v0.0.0-20221115062448-fe3a3abad311/go.mod h1:b583jCggY9gE99b6G5LEC39OIiVsWj+R97kbl5odCEk=
 github.com/chzyer/logex v1.1.10/go.mod h1:+Ywpsq7O8HXn0nuIou7OrIPyXbp3wmkHB+jjWRnGsAI=
 github.com/chzyer/readline v0.0.0-20180603132655-2972be24d48e/go.mod h1:nSuG5e5PlCu98SY8svDHJxuZscDgtXS6KTTbou5AhLI=
 github.com/chzyer/readline v1.5.1 h1:upd/6fQk4src78LMRzh5vItIt361/o4uq553V8B5sGI=
@@ -268,8 +276,8 @@ github.com/getsentry/sentry-go v0.20.0/go.mod h1:lc76E2QywIyW8WuBnwl8Lc4bkmQH4+w
 github.com/ghodss/yaml v1.0.0/go.mod h1:4dBDuWmgqj2HViK6kFavaiC9ZROes6MMH2rRYeMEF04=
 github.com/gin-contrib/sse v0.1.0 h1:Y/yl/+YNO8GZSjAhjMsSuLt29uWRFHdHYUb5lYOV9qE=
 github.com/gin-contrib/sse v0.1.0/go.mod h1:RHrZQHXnP2xjPF+u1gW/2HnVO7nvIa9PG3Gm+fLHvGI=
-github.com/gin-gonic/gin v1.8.1 h1:4+fr/el88TOO3ewCmQr8cx/CtZ/umlIRIs5M4NTNjf8=
-github.com/gin-gonic/gin v1.8.1/go.mod h1:ji8BvRH1azfM+SYow9zQ6SZMvR8qOMZHmsCuWR9tTTk=
+github.com/gin-gonic/gin v1.9.0 h1:OjyFBKICoexlu99ctXNR2gg+c5pKrKMuyjgARg9qeY8=
+github.com/gin-gonic/gin v1.9.0/go.mod h1:W1Me9+hsUSyj3CePGrd1/QrKJMSJ1Tu/0hFEH89961k=
 github.com/go-check/check v0.0.0-20180628173108-788fd7840127/go.mod h1:9ES+weclKsC9YodN5RgxqK/VD9HM9JsCSh7rNhMZE98=
 github.com/go-errors/errors v1.0.1/go.mod h1:f4zRHt4oKfwPJE5k8C9vpYG+aDHdBFUsgrm6/TyX73Q=
 github.com/go-errors/errors v1.4.2 h1:J6MZopCL4uSllY1OfXM374weqZFFItUbrImctkmUxIA=
@@ -290,13 +298,13 @@ github.com/go-logfmt/logfmt v0.5.0/go.mod h1:wCYkCAKZfumFQihp8CzCvQ3paCTfi41vtzG
 github.com/go-logfmt/logfmt v0.6.0 h1:wGYYu3uicYdqXVgoYbvnkrPVXkuLM1p1ifugDMEdRi4=
 github.com/go-logfmt/logfmt v0.6.0/go.mod h1:WYhtIu8zTZfxdn5+rREduYbwxfcBr/Vr6KEVveWlfTs=
 github.com/go-martini/martini v0.0.0-20170121215854-22fa46961aab/go.mod h1:/P9AEU963A2AYjv4d1V5eVL1CQbEJq6aCNHDDjibzu8=
-github.com/go-playground/assert/v2 v2.0.1/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
-github.com/go-playground/locales v0.14.0 h1:u50s323jtVGugKlcYeyzC0etD1HifMjqmJqb8WugfUU=
-github.com/go-playground/locales v0.14.0/go.mod h1:sawfccIbzZTqEDETgFXqTho0QybSa7l++s0DH+LDiLs=
-github.com/go-playground/universal-translator v0.18.0 h1:82dyy6p4OuJq4/CByFNOn/jYrnRPArHwAcmLoJZxyho=
-github.com/go-playground/universal-translator v0.18.0/go.mod h1:UvRDBj+xPUEGrFYl+lu/H90nyDXpg0fqeB/AQUGNTVA=
-github.com/go-playground/validator/v10 v10.10.0/go.mod h1:74x4gJWsvQexRdW8Pn3dXSGrTK4nAUsbPlLADvpJkos=
-github.com/go-playground/validator/v10 v10.11.1 h1:prmOlTVv+YjZjmRmNSF3VmspqJIxJWXmqUsHwfTRRkQ=
+github.com/go-playground/assert/v2 v2.2.0/go.mod h1:VDjEfimB/XKnb+ZQfWdccd7VUvScMdVu0Titje2rxJ4=
+github.com/go-playground/locales v0.14.1 h1:EWaQ/wswjilfKLTECiXz7Rh+3BjFhfDFKv/oXslEjJA=
+github.com/go-playground/locales v0.14.1/go.mod h1:hxrqLVvrK65+Rwrd5Fc6F2O76J/NuW9t0sjnWqG1slY=
+github.com/go-playground/universal-translator v0.18.1 h1:Bcnm0ZwsGyWbCzImXv+pAJnYK9S473LQFuzCbDbfSFY=
+github.com/go-playground/universal-translator v0.18.1/go.mod h1:xekY+UJKNuX9WP91TpwSH2VMlDf28Uj24BCp08ZFTUY=
+github.com/go-playground/validator/v10 v10.11.2 h1:q3SHpufmypg+erIExEKUmsgmhDTyhcJ38oeKGACXohU=
+github.com/go-playground/validator/v10 v10.11.2/go.mod h1:NieE624vt4SCTJtD87arVLvdmjPAeV8BQlHtMnw9D7s=
 github.com/go-sql-driver/mysql v1.4.0/go.mod h1:zAC/RDZ24gD3HViQzih4MyKcchzm+sOG5ZlKdlhCg5w=
 github.com/go-stack/stack v1.8.0/go.mod h1:v0f6uXyyMGvRgIKkXu+yp6POWl0qKG85gN/melR3HDY=
 github.com/go-task/slim-sprig v0.0.0-20210107165309-348f09dbbbc0/go.mod h1:fyg7847qk6SyHyPtNmDHnmrv/HOrqktSC+C9fM+CJOE=
@@ -306,8 +314,8 @@ github.com/gobwas/pool v0.2.0 h1:QEmUOlnSjWtnpRGHF3SauEiOsy82Cup83Vf2LcMlnc8=
 github.com/gobwas/pool v0.2.0/go.mod h1:q8bcK0KcYlCgd9e7WYLm9LpyS+YeLd8JVDW6WezmKEw=
 github.com/gobwas/ws v1.0.2 h1:CoAavW/wd/kulfZmSIBt6p24n4j7tHgNVCjsfHVNUbo=
 github.com/gobwas/ws v1.0.2/go.mod h1:szmBTxLgaFppYjEmNtny/v3w89xOydFnnZMcgRRu/EM=
-github.com/goccy/go-json v0.9.7/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
-github.com/goccy/go-json v0.9.11 h1:/pAaQDLHEoCq/5FFmSKBswWmK6H0e8g4159Kc/X/nqk=
+github.com/goccy/go-json v0.10.0 h1:mXKd9Qw4NuzShiRlOXKews24ufknHO7gx30lsDyokKA=
+github.com/goccy/go-json v0.10.0/go.mod h1:6MelG93GURQebXPDq3khkgXZkazVtN9CRI+MGFi0w8I=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2 h1:ZpnhV/YsD2/4cESfV5+Hoeu/iUR3ruzNvZ+yQfO03a0=
 github.com/godbus/dbus v0.0.0-20190726142602-4481cbc300e2/go.mod h1:bBOAhwG1umN6/6ZUMtDFBMQR8jRg9O75tm9K00oMsK4=
 github.com/godbus/dbus/v5 v5.0.4/go.mod h1:xhWf0FNVPg57R7Z0UbKHbJfkEywrmjJnf7w5xrFpKfA=
@@ -530,7 +538,10 @@ github.com/klauspost/compress v1.11.7/go.mod h1:aoV0uJVorq1K+umq18yTdKaF57EivdYs
 github.com/klauspost/compress v1.12.3/go.mod h1:8dP1Hq4DHOhN9w426knH3Rhby4rFm6D8eO+e+Dq5Gzg=
 github.com/klauspost/compress v1.16.5 h1:IFV2oUNUzZaz+XyusxpLzpzS8Pt5rh0Z16For/djlyI=
 github.com/klauspost/compress v1.16.5/go.mod h1:ntbaceVETuRiXiv4DpjP66DpAtAGkEQskQzEyD//IeE=
+github.com/klauspost/cpuid v1.2.1 h1:vJi+O/nMdFt0vqm8NZBI6wzALWdA2X+egi0ogNyrC/w=
 github.com/klauspost/cpuid v1.2.1/go.mod h1:Pj4uuM528wm8OyEC2QMXAi2YiTZ96dNQPGgoMS4s3ek=
+github.com/klauspost/cpuid/v2 v2.0.9 h1:lgaqFMSdTdQYdZ04uHyN2d/eKdOMyi2YLSvlQIBFYa4=
+github.com/klauspost/cpuid/v2 v2.0.9/go.mod h1:FInQzS24/EEf25PyTYn52gqo7WaD8xa0213Md/qVLRg=
 github.com/konsorten/go-windows-terminal-sequences v1.0.1/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/konsorten/go-windows-terminal-sequences v1.0.3/go.mod h1:T0+1ngSBFLxvqU3pZ+m/2kptfBszLMUkC4ZK/EgS/cQ=
 github.com/kr/fs v0.1.0/go.mod h1:FFnZGqtBN9Gxj7eW1uZ42v5BccTP0vu6NEaFoC2HwRg=
@@ -576,6 +587,7 @@ github.com/mattn/go-isatty v0.0.9/go.mod h1:YNRxwqDuOph6SZLI9vUUz6OYw3QyUt7WiY2y
 github.com/mattn/go-isatty v0.0.12/go.mod h1:cbi8OIDigv2wuxKPP5vlRcQ1OAZbq2CE4Kysco4FUpU=
 github.com/mattn/go-isatty v0.0.14/go.mod h1:7GGIvUiUoEMVVmxf/4nioHXj79iQHKdU27kJ6hsGG94=
 github.com/mattn/go-isatty v0.0.16/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
+github.com/mattn/go-isatty v0.0.17/go.mod h1:kYGgaQfpe5nmfYZH+SKPsOc2e4SrIfOl2e/yFXSvRLM=
 github.com/mattn/go-isatty v0.0.18 h1:DOKFKCQ7FNG2L1rbrmstDN4QVRdS89Nkh85u68Uwp98=
 github.com/mattn/go-isatty v0.0.18/go.mod h1:W+V8PltTTMOvKvAeJH7IuucS94S2C6jfK/D7dTCTo3Y=
 github.com/mattn/go-runewidth v0.0.2/go.mod h1:LwmH8dsx7+W8Uxz3IHJYH5QSwggIsqBzpuz5H//U1FU=
@@ -666,7 +678,7 @@ github.com/pascaldekloe/goe v0.1.0 h1:cBOtyMzM9HTpWjXfbbunk26uA6nG3a8n06Wieeh0Mw
 github.com/pascaldekloe/goe v0.1.0/go.mod h1:lzWF7FIEvWOWxwDKqyGYQf6ZUaNfKdP144TG7ZOy1lc=
 github.com/pborman/uuid v1.2.0/go.mod h1:X/NO0urCmaxf9VXbdlT7C2Yzkj2IKimNn4k+gtPdI/k=
 github.com/pelletier/go-toml v1.2.0/go.mod h1:5z9KED0ma1S8pY6P1sdut58dfprrGBbd/94hg7ilaic=
-github.com/pelletier/go-toml/v2 v2.0.1/go.mod h1:r9LEWfGN8R5k0VXJ+0BkIe7MYkRdwZOjgMj2KwnJFUo=
+github.com/pelletier/go-toml/v2 v2.0.6/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/pelletier/go-toml/v2 v2.0.7 h1:muncTPStnKRos5dpVKULv2FVd4bMOhNePj9CjgDb8Us=
 github.com/pelletier/go-toml/v2 v2.0.7/go.mod h1:eumQOmlWiOPt5WriQQqoM5y18pDHwha2N+QD+EUNTek=
 github.com/performancecopilot/speed v3.0.0+incompatible/go.mod h1:/CLtqpZ5gBg1M9iaPbIdPPGyKcA8hKdoy6hAWba7Yac=
@@ -814,13 +826,14 @@ github.com/tidwall/btree v1.6.0 h1:LDZfKfQIBHGHWSwckhXI0RPSXzlo+KYdjK7FWSqOzzg=
 github.com/tidwall/btree v1.6.0/go.mod h1:twD9XRA5jj9VUQGELzDO4HPQTNJsoWWfYEL+EUQ2cKY=
 github.com/tmc/grpc-websocket-proxy v0.0.0-20170815181823-89b8d40f7ca8/go.mod h1:ncp9v5uamzpCO7NfCPTXjqaC+bZgJeR0sMTm6dMHP7U=
 github.com/tv42/httpunix v0.0.0-20150427012821-b75d8614f926/go.mod h1:9ESjWnEqriFuLhtthL60Sar/7RFoluCcXsuvEwTV5KM=
+github.com/twitchyliquid64/golang-asm v0.15.1 h1:SU5vSMR7hnwNxj24w34ZyCi/FmDZTkS4MhqMhdFk5YI=
+github.com/twitchyliquid64/golang-asm v0.15.1/go.mod h1:a1lVb/DtPvCB8fslRZhAngC2+aY1QWCk3Cedj/Gdt08=
+github.com/ugorji/go v1.1.7 h1:/68gy2h+1mWMrwZFeD1kQialdSzAb432dtpeJ42ovdo=
 github.com/ugorji/go v1.1.7/go.mod h1:kZn38zHttfInRq0xu/PH0az30d+z6vm202qpg1oXVMw=
-github.com/ugorji/go v1.2.7 h1:qYhyWUUd6WbiM+C6JZAUkIJt/1WrjzNHY9+KCIjVqTo=
-github.com/ugorji/go v1.2.7/go.mod h1:nF9osbDWLy6bDVv/Rtoh6QgnvNDpmCalQV5urGCCS6M=
 github.com/ugorji/go/codec v0.0.0-20181204163529-d75b2dcb6bc8/go.mod h1:VFNgLljTbGfSG7qAOspJ7OScBnGdDN/yBr0sguwnwf0=
 github.com/ugorji/go/codec v1.1.7/go.mod h1:Ax+UKWsSmolVDwsd+7N3ZtXu+yMGCf907BLYF3GoBXY=
-github.com/ugorji/go/codec v1.2.7 h1:YPXUKf7fYbp/y8xloBqZOw2qaVggbfwMlI8WM3wZUJ0=
-github.com/ugorji/go/codec v1.2.7/go.mod h1:WGN1fab3R1fzQlVQTkfxVtIBhWDRqOviHU95kRgeqEY=
+github.com/ugorji/go/codec v1.2.9 h1:rmenucSohSTiyL09Y+l2OCk+FrMxGMzho2+tjr5ticU=
+github.com/ugorji/go/codec v1.2.9/go.mod h1:UNopzCgEMSXjBc6AOMqYvWC1ktqTAfzJZUZgYf6w6lg=
 github.com/urfave/cli v1.20.0/go.mod h1:70zkFmudgCuE/ngEzBv17Jvp/497gISqfk5gWijbERA=
 github.com/urfave/cli v1.22.1/go.mod h1:Gos4lmkARVdJ6EkW0WaNv/tZAAMe9V7XWyB60NtXRu0=
 github.com/urfave/negroni v1.0.0/go.mod h1:Meg73S6kFm/4PpbYdq35yYWoCZ9mS/YSx+lKnmiohz4=
@@ -843,6 +856,7 @@ github.com/yuin/goldmark v1.1.27/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9de
 github.com/yuin/goldmark v1.1.32/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.2.1/go.mod h1:3hX8gzYuyVAZsxl0MRgGTJEmQBFcNTphYh9decYSb74=
 github.com/yuin/goldmark v1.3.5/go.mod h1:mwnBkeHKe2W/ZEtQ+71ViKU8L12m81fl3OWwC1Zlc8k=
+github.com/yuin/goldmark v1.4.13/go.mod h1:6yULJ656Px+3vBD8DxQVa3kxgyrAnzto9xy5taEt/CY=
 github.com/zondax/hid v0.9.1 h1:gQe66rtmyZ8VeGFcOpbuH3r7erYtNEAezCAYu8LdkJo=
 github.com/zondax/hid v0.9.1/go.mod h1:l5wttcP0jwtdLjqjMMWFVEE7d1zO0jvSPA9OPZxWpEM=
 github.com/zondax/ledger-go v0.14.1 h1:Pip65OOl4iJ84WTpA4BKChvOufMhhbxED3BaihoZN4c=
@@ -872,6 +886,8 @@ go.uber.org/tools v0.0.0-20190618225709-2cfd321de3ee/go.mod h1:vJERXedbb3MVM5f9E
 go.uber.org/zap v1.10.0/go.mod h1:vwi/ZaCAaUcBkycHslxD9B2zi4UTXhF60s6SWpuDF0Q=
 go.uber.org/zap v1.13.0/go.mod h1:zwrFLgMcdUuIBviXEYEH1YKNaOBnKXsx2IPda5bBwHM=
 go.uber.org/zap v1.18.1/go.mod h1:xg/QME4nWcxGxrpdeYfq7UvYrLh66cuVKdrbD1XF/NI=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670 h1:18EFjUmQOcUvxNYSkA6jO9VAiXCnxFY6NyDX0bHDmkU=
+golang.org/x/arch v0.0.0-20210923205945-b76863e36670/go.mod h1:5om86z9Hs0C8fWVUuoMHwpExlXzs5Tkyp9hOrfG7pp8=
 golang.org/x/crypto v0.0.0-20180904163835-0709b304e793/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181029021203-45a5f77698d3/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
 golang.org/x/crypto v0.0.0-20181203042331-505ab145d0a9/go.mod h1:6SG95UA2DQfeDnfUPMdvaQW0Q7yPrPDi9nlGo2tz2b4=
@@ -886,9 +902,9 @@ golang.org/x/crypto v0.0.0-20200622213623-75b288015ac9/go.mod h1:LzIPMQfyMNhhGPh
 golang.org/x/crypto v0.0.0-20200728195943-123391ffb6de/go.mod h1:LzIPMQfyMNhhGPhUkYOs5KpL4U8rLKemX1yGLhDgUto=
 golang.org/x/crypto v0.0.0-20210322153248-0c34fe9e7dc2/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
 golang.org/x/crypto v0.0.0-20210421170649-83a5a9bb288b/go.mod h1:T9bdIzuCu7OtxOm1hfPfRQxPLYneinmdGuTeoZ9dtd4=
-golang.org/x/crypto v0.0.0-20210711020723-a769d52b0f97/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20210921155107-089bfa567519/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
 golang.org/x/crypto v0.0.0-20211108221036-ceb1ce70b4fa/go.mod h1:GvvjBRRGRdwPK5ydBHafDWAxML/pGHZbMvKqRZ5+Abc=
+golang.org/x/crypto v0.5.0/go.mod h1:NK/OQwhpMQP3MwtdjgLlYHnH9ebylxKWv3e0fK+mkQU=
 golang.org/x/crypto v0.9.0 h1:LF6fAI+IutBocDJ2OT0Q1g8plpYljMZ4+lty+dsqw3g=
 golang.org/x/crypto v0.9.0/go.mod h1:yrmDGqONDYtNj3tH8X9dzUun2m2lzPa9ngI6/RUPGR0=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
@@ -929,6 +945,7 @@ golang.org/x/mod v0.3.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.0/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.1/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
 golang.org/x/mod v0.4.2/go.mod h1:s0Qsj1ACt9ePp/hMypM3fl4fZqREWJwdYDEqhRiZZUA=
+golang.org/x/mod v0.6.0-dev.0.20220419223038-86c51ed26bb4/go.mod h1:jJ57K6gSWd91VN4djpZkiMVwK6gcyfeH4XE8wZrZaV4=
 golang.org/x/mod v0.8.0 h1:LUYupSeNrTNCGzR/hVBk2NHZO4hXcVaW1k4Qx7rjPx8=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -979,6 +996,9 @@ golang.org/x/net v0.0.0-20210805182204-aaa1db679c0d/go.mod h1:9nx3DQGgdP8bBQD5qx
 golang.org/x/net v0.0.0-20211008194852-3b03d305991f/go.mod h1:9nx3DQGgdP8bBQD5qxJ1jj9UTztislL4KSBs9R2vV5Y=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
+golang.org/x/net v0.0.0-20220722155237-a158d28d115b/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
+golang.org/x/net v0.5.0/go.mod h1:DivGGAXEgPSlEBzxGzZI+ZLohi+xUj054jfeKui00ws=
+golang.org/x/net v0.7.0/go.mod h1:2Tu9+aMcznHK/AK1HMvgo6xiTLG5rD5rZLDS+rp2Bjs=
 golang.org/x/net v0.10.0 h1:X2//UzNDwYmtCLn7To6G58Wr6f5ahEAQgKNzv9Y951M=
 golang.org/x/net v0.10.0/go.mod h1:0qNGK6F8kojg2nk9dLZ2mShWaEBan6FAoqfSigmmuDg=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
@@ -1001,6 +1021,7 @@ golang.org/x/sync v0.0.0-20200625203802-6e8e738ad208/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20201207232520-09787c993a3a/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20210220032951-036812b2e83c/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
+golang.org/x/sync v0.0.0-20220722155255-886fb9371eb4/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.2.0 h1:PUR+T4wwASmuSTYdKjYHI5TD22Wy5ogLU5qZCOLxBrI=
 golang.org/x/sync v0.2.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -1068,7 +1089,6 @@ golang.org/x/sys v0.0.0-20210423185535-09eb48e85fd7/go.mod h1:h1NjWce9XRLGQEsW7w
 golang.org/x/sys v0.0.0-20210510120138-977fb7262007/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210615035016-665e8c7367d1/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210630005230-0f9fa26af87c/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.0.0-20210806184541-e5e7981a1069/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210809222454-d867a43fc93e/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210819135213-f52c844e1c1c/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20210927094055-39ccf1dd6fa6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
@@ -1080,14 +1100,19 @@ golang.org/x/sys v0.0.0-20220315194320-039c03cc5b86/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220503163025-988cb79eb6c6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.0.0-20220722155257-8c9f86f7a55f/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20221010170243-090e33056c14/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.4.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.5.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.8.0 h1:EBmGv8NaZBZTWvrbjNoL6HVt+IVy3QDQpJs7VRIw3tU=
 golang.org/x/sys v0.8.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
+golang.org/x/term v0.4.0/go.mod h1:9P2UbLfCdcvo3p/nzKvsmas4TnlujnuoV9hGgYzW1lQ=
+golang.org/x/term v0.5.0/go.mod h1:jMB1sMXY+tzblOD4FWmEbocvup2/aLOaQEp7JmGp78k=
 golang.org/x/term v0.8.0 h1:n5xxQn2i3PC0yLAbjTpNT85q/Kgzcr2gIoX9OrJUols=
 golang.org/x/term v0.8.0/go.mod h1:xPskH00ivmX89bAKVGSKKtLOWNx2+17Eiy94tnKShWo=
 golang.org/x/text v0.0.0-20170915032832-14c0d48ead0c/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
@@ -1099,6 +1124,9 @@ golang.org/x/text v0.3.4/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.5/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
+golang.org/x/text v0.3.8/go.mod h1:E6s5w1FMmriuDzIBO73fBruAKo1PCIq6d2Q6DHfQ8WQ=
+golang.org/x/text v0.6.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
+golang.org/x/text v0.7.0/go.mod h1:mrYo+phRRbMaCq/xk9113O4dZlRixOauAjOtrjsXDZ8=
 golang.org/x/text v0.9.0 h1:2sjJmO8cDvYveuX97RDLsxlyUxLl+GHoLxBiRdHllBE=
 golang.org/x/text v0.9.0/go.mod h1:e1OnstbJyHTd6l/uOt8jFFHp6TRDWZR/bV3emEE/zU8=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -1168,6 +1196,7 @@ golang.org/x/tools v0.0.0-20210108195828-e2f9c7f1fc8e/go.mod h1:emZCQorbCU4vsT4f
 golang.org/x/tools v0.1.0/go.mod h1:xkSsbof2nBLbhDlRMhhhyNLN/zl3eTqcnHD5viDpcZ0=
 golang.org/x/tools v0.1.1/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
 golang.org/x/tools v0.1.3/go.mod h1:o0xws9oXOQQZyjljx8fwUC0k7L1pTE6eaCbjGeHmOkk=
+golang.org/x/tools v0.1.12/go.mod h1:hNGJHUnrk76NpqgfD5Aqm5Crs+Hm0VOH/i9J2+nxYbc=
 golang.org/x/tools v0.6.0 h1:BOw41kyTf3PuCW1pVQf8+Cyg8pMlkYB1oo9iJ6D/lKM=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
@@ -1291,7 +1320,6 @@ google.golang.org/protobuf v1.25.0/go.mod h1:9JNX74DMeImyA3h4bdi1ymwjUzf21/xIlba
 google.golang.org/protobuf v1.26.0-rc.1/go.mod h1:jlhhOSvTdKEhbULTjvd4ARK9grFBp09yW+WbY/TyQbw=
 google.golang.org/protobuf v1.26.0/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
 google.golang.org/protobuf v1.27.1/go.mod h1:9q0QmTI4eRPtz6boOQmLYwt+qCgq0jsYwAQnmE0givc=
-google.golang.org/protobuf v1.28.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 google.golang.org/protobuf v1.28.1/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
 google.golang.org/protobuf v1.30.0 h1:kPPoIgf3TsEvrm0PFe15JQ+570QVxYzEvvHqChK+cng=
 google.golang.org/protobuf v1.30.0/go.mod h1:HV8QOd/L58Z+nl8r43ehVNZIU/HEI6OcFqwMG9pJV4I=
@@ -1344,6 +1372,7 @@ nhooyr.io/websocket v1.8.6/go.mod h1:B70DZP8IakI65RVQ51MsWP/8jndNma26DVA/nFSCgW0
 pgregory.net/rapid v0.5.7 h1:p7/XbOgyFY1I/3Q12UTXfos70VZTcgc3WeoyiEru5cs=
 pgregory.net/rapid v0.5.7/go.mod h1:PY5XlDGj0+V1FCq0o192FdRhpKHGTRIWBgqjDBTrq04=
 rsc.io/binaryregexp v0.2.0/go.mod h1:qTv7/COck+e2FymRvadv62gMdZztPaShugOCi3I+8D8=
+rsc.io/pdf v0.1.1/go.mod h1:n8OzWcQ6Sp37PL01nO98y4iUCRdTGarVfzxY20ICaU4=
 rsc.io/quote/v3 v3.1.0/go.mod h1:yEA65RcK8LyAZtP9Kv3t0HmxON59tX3rD+tICJqUlj0=
 rsc.io/sampler v1.3.0/go.mod h1:T1hPZKmBbMNahiBKFy5HrXp6adAjACjK9JXDnKaTXpA=
 sigs.k8s.io/yaml v1.1.0/go.mod h1:UJmg0vDUVViEyp3mgSv9WPwZCDxu4rQW1olrI1uml+o=
```
