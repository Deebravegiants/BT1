# [?] go: Add CVE-2025-4673 to .nancy-ignore for now

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2025-06-14
Source: https://github.com/oasisprotocol/oasis-core/commit/da8c5a71021a37e03b71965eef9e57a7fd6adce3
Type: security-commit

## Details
go: Add CVE-2025-4673 to .nancy-ignore for now

The vulnerability does not affect our use of the library and no
mitigation is currently available.

## Patch
### go/.nancy-ignore
```diff
@@ -1,2 +1,2 @@
 CVE-2024-34478 # can be ignored as we only use a few crypto libraries from btcd
-CVE-2024-8421 until=2024-10-01  # no mitigation is currently available (2024-09-06)
+CVE-2025-4673 until=2025-07-14  # no mitigation is currently available (2025-06-14)
```

### go/go.mod
```diff
@@ -55,9 +55,9 @@ require (
 	github.com/tidwall/btree v1.6.0
 	github.com/tyler-smith/go-bip39 v1.1.0
 	go.uber.org/zap v1.27.0
-	golang.org/x/crypto v0.36.0
+	golang.org/x/crypto v0.39.0
 	golang.org/x/exp v0.0.0-20250128182459-e0ece0dbea4c
-	golang.org/x/net v0.38.0
+	golang.org/x/net v0.41.0
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20240903143218-8af14fe29dc1
 	google.golang.org/grpc v1.68.0
 	google.golang.org/grpc/security/advancedtls v0.0.0-20221004221323-12db695f1648
@@ -209,11 +209,11 @@ require (
 	go.uber.org/fx v1.23.0 // indirect
 	go.uber.org/mock v0.5.0 // indirect
 	go.uber.org/multierr v1.11.0 // indirect
-	golang.org/x/mod v0.23.0 // indirect
-	golang.org/x/sync v0.12.0 // indirect
-	golang.org/x/sys v0.31.0 // indirect
-	golang.org/x/text v0.23.0 // indirect
-	golang.org/x/tools v0.29.0 // indirect
+	golang.org/x/mod v0.25.0 // indirect
+	golang.org/x/sync v0.15.0 // indirect
+	golang.org/x/sys v0.33.0 // indirect
+	golang.org/x/text v0.26.0 // indirect
+	golang.org/x/tools v0.33.0 // indirect
 	gopkg.in/fsnotify.v1 v1.4.7 // indirect
 	gopkg.in/ini.v1 v1.67.0 // indirect
 	gopkg.in/tomb.v1 v1.0.0-20141024135613-dd632973f1e7 // indirect
```

### go/go.sum
```diff
@@ -1793,8 +1793,8 @@ golang.org/x/crypto v0.11.0/go.mod h1:xgJhtzW8F9jGdVFWZESrid1U1bjeNy4zgy5cRr/CIi
 golang.org/x/crypto v0.12.0/go.mod h1:NF0Gs7EO5K4qLn+Ylc+fih8BSTeIjAP05siRnAh98yw=
 golang.org/x/crypto v0.13.0/go.mod h1:y6Z2r+Rw4iayiXXAIxJIDAJ1zMW4yaTpebo8fPOliYc=
 golang.org/x/crypto v0.18.0/go.mod h1:R0j02AL6hcrfOiy9T4ZYp/rcWeMxM3L6QYxlOuEG1mg=
-golang.org/x/crypto v0.36.0 h1:AnAEvhDddvBdpY+uR+MyHmuZzzNqXSe/GvuDeob5L34=
-golang.org/x/crypto v0.36.0/go.mod h1:Y4J0ReaxCR1IMaabaSMugxJES1EpwhBHhv2bDHklZvc=
+golang.org/x/crypto v0.39.0 h1:SHs+kF4LP+f+p14esP5jAoDpHU8Gu/v9lFRK6IT5imM=
+golang.org/x/crypto v0.39.0/go.mod h1:L+Xg3Wf6HoL4Bn4238Z6ft6KfEpN0tJGo53AAPC632U=
 golang.org/x/exp v0.0.0-20180321215751-8460e604b9de/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20180807140117-3d87b88a115f/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
 golang.org/x/exp v0.0.0-20190121172915-509febef88a4/go.mod h1:CJ0aWSM057203Lf6IL+f9T1iT9GByDxfZKAQTCR3kQA=
@@ -1861,8 +1861,8 @@ golang.org/x/mod v0.9.0/go.mod h1:iBbtSCu2XBx23ZKBPSOrRkjjQPZFPuis4dIYUhu/chs=
 golang.org/x/mod v0.10.0/go.mod h1:iBbtSCu2XBx23ZKBPSOrRkjjQPZFPuis4dIYUhu/chs=
 golang.org/x/mod v0.11.0/go.mod h1:iBbtSCu2XBx23ZKBPSOrRkjjQPZFPuis4dIYUhu/chs=
 golang.org/x/mod v0.12.0/go.mod h1:iBbtSCu2XBx23ZKBPSOrRkjjQPZFPuis4dIYUhu/chs=
-golang.org/x/mod v0.23.0 h1:Zb7khfcRGKk+kqfxFaP5tZqCnDZMjC5VtUBs87Hr6QM=
-golang.org/x/mod v0.23.0/go.mod h1:6SkKJ3Xj0I0BrPOZoBy3bdMptDDU9oJrpohJ3eWZ1fY=
+golang.org/x/mod v0.25.0 h1:n7a+ZbQKQA/Ysbyb0/6IbB1H/X41mKgbhfv7AfG/44w=
+golang.org/x/mod v0.25.0/go.mod h1:IXM97Txy2VM4PJ3gI61r1YEk/gAj6zAHN3AdZt6S9Ww=
 golang.org/x/net v0.0.0-20180724234803-3673e40ba225/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180826012351-8a410e7b638d/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
 golang.org/x/net v0.0.0-20180906233101-161cd47e91fd/go.mod h1:mL1N/T3taQHkDXs73rZJwtUhF3w3ftmwwsq0BUmARs4=
@@ -1939,8 +1939,8 @@ golang.org/x/net v0.13.0/go.mod h1:zEVYFnQC7m/vmpQFELhcD1EWkZlX69l4oqgmer6hfKA=
 golang.org/x/net v0.14.0/go.mod h1:PpSgVXXLK0OxS0F31C1/tv6XNguvCrnXIDrFMspZIUI=
 golang.org/x/net v0.15.0/go.mod h1:idbUs1IY1+zTqbi8yxTbhexhEEk5ur9LInksu6HrEpk=
 golang.org/x/net v0.20.0/go.mod h1:z8BVo6PvndSri0LbOE3hAn0apkU+1YvI6E70E9jsnvY=
-golang.org/x/net v0.38.0 h1:vRMAPTMaeGqVhG5QyLJHqNDwecKTomGeqbnfZyKlBI8=
-golang.org/x/net v0.38.0/go.mod h1:ivrbrMbzFq5J41QOQh0siUuly180yBYtLp+CKbEaFx8=
+golang.org/x/net v0.41.0 h1:vBTly1HeNPEn3wtREYfy4GZ/NECgw2Cnl+nK6Nz3uvw=
+golang.org/x/net v0.41.0/go.mod h1:B/K4NNqkfmg07DQYrbwvSluqCJOOXwUjeb/5lOisjbA=
 golang.org/x/oauth2 v0.0.0-20180821212333-d2e6202438be/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20181017192945-9dcd33a902f4/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
 golang.org/x/oauth2 v0.0.0-20181203162652-d668ce993890/go.mod h1:N/0e6XlmueqKjAGxoOufVs8QHGRruUQn6yWY3a++T0U=
@@ -1996,8 +1996,8 @@ golang.org/x/sync v0.0.0-20220929204114-8fcdb60fdcc0/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sync v0.1.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.2.0/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.3.0/go.mod h1:FU7BRWz2tNW+3quACPkgCx/L+uEAv1htQ0V83Z9Rj+Y=
-golang.org/x/sync v0.12.0 h1:MHc5BpPuC30uJk597Ri8TV3CNZcTLu6B6z4lJy+g6Jw=
-golang.org/x/sync v0.12.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
+golang.org/x/sync v0.15.0 h1:KWH3jNZsfyT6xfAfKiz6MRNmd46ByHDYaZ7KSkCtdW8=
+golang.org/x/sync v0.15.0/go.mod h1:1dzgHSNfp02xaA81J2MS99Qcpr2w7fw1gpm99rleRqA=
 golang.org/x/sys v0.0.0-20180810173357-98c5dad5d1a0/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180823144017-11551d06cbcc/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20180830151530-49385e6e1522/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
@@ -2114,8 +2114,8 @@ golang.org/x/sys v0.11.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.12.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.16.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/sys v0.21.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
-golang.org/x/sys v0.31.0 h1:ioabZlmFYtWhL+TRYpcnNlLwhyxaM9kWTDEmfnprqik=
-golang.org/x/sys v0.31.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
+golang.org/x/sys v0.33.0 h1:q3i8TbbEz+JRD9ywIRlyRAQbM0qF7hu24q3teo2hbuw=
+golang.org/x/sys v0.33.0/go.mod h1:BJP2sWEmIv4KK5OTEluFJCKSidICx8ciO85XgH3Ak8k=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/term v0.1.0/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
@@ -2152,8 +2152,8 @@ golang.org/x/text v0.11.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
 golang.org/x/text v0.12.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
 golang.org/x/text v0.13.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
 golang.org/x/text v0.14.0/go.mod h1:18ZOQIKpY8NJVqYksKHtTdi31H5itFRjB5/qKTNYzSU=
-golang.org/x/text v0.23.0 h1:D71I7dUrlY+VX0gQShAThNGHFxZ13dGLBHQLVl1mJlY=
-golang.org/x/text v0.23.0/go.mod h1:/BLNzu4aZCJ1+kcD0DNRotWKage4q2rGVAg4o22unh4=
+golang.org/x/text v0.26.0 h1:P42AVeLghgTYr4+xUnTRKDMqpar+PtX7KWuNQL21L8M=
+golang.org/x/text v0.26.0/go.mod h1:QK15LZJUUQVJxhz7wXgxSy/CJaTFjd0G+YLonydOVQA=
 golang.org/x/time v0.0.0-20180412165947-fbb02b2291d2/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20181108054448-85acf8d2951c/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
 golang.org/x/time v0.0.0-20190308202827-9d24e82272b4/go.mod h1:tRJNPiyCQ0inRvYxbN9jk5I+vvW/OXSQhTDSoE431IQ=
@@ -2236,8 +2236,8 @@ golang.org/x/tools v0.8.0/go.mod h1:JxBZ99ISMI5ViVkT1tr6tdNmXeTrcpVSD3vZ1RsRdN4=
 golang.org/x/tools v0.9.1/go.mod h1:owI94Op576fPu3cIGQeHs3joujW/2Oc6MtlxbF5dfNc=
 golang.org/x/tools v0.10.0/go.mod h1:UJwyiVBsOA2uwvK/e5OY3GTpDUJriEd+/YlqAwLPmyM=
 golang.org/x/tools v0.13.0/go.mod h1:HvlwmtVNQAhOuCjW7xxvovg8wbNq7LwfXh/k7wXUl58=
-golang.org/x/tools v0.29.0 h1:Xx0h3TtM9rzQpQuR4dKLrdglAmCEN5Oi+P74JdhdzXE=
-golang.org/x/tools v0.29.0/go.mod h1:KMQVMRsVxU6nHCFXrBPhDB8XncLNLM0lIy/F14RP588=
+golang.org/x/tools v0.33.0 h1:4qz2S3zmRxbGIhDIAgjxvFutSvH5EfnsYrRBj0UI0bc=
+golang.org/x/tools v0.33.0/go.mod h1:CIJMaWEY88juyUfo7UbgPqbC8rU2OqfAV1h2Qp0oMYI=
 golang.org/x/xerrors v0.0.0-20190717185122-a985d3407aa7/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
```
