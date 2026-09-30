# [?] build(deps): update grpc, net dependencies per vulnerability advisories (#18617)

## Summary
Severity: Unknown
Chain: Cosmos
Component: cosmos/cosmos-sdk
Published: 2023-12-03
Source: https://github.com/cosmos/cosmos-sdk/commit/e049998eb5f2582fe0bb5ab102f0de87b1466534
Type: security-commit

## Details
build(deps): update grpc, net dependencies per vulnerability advisories (#18617)

## Patch
### api/go.mod
```diff
@@ -5,7 +5,7 @@ go 1.20
 require (
 	github.com/cosmos/cosmos-proto v1.0.0-beta.3
 	github.com/cosmos/gogoproto v1.4.11
-	google.golang.org/genproto/googleapis/api v0.0.0-20231002182017-d307bd883b97
+	google.golang.org/genproto/googleapis/api v0.0.0-20231106174013-bbf56f31fb17
 	google.golang.org/grpc v1.59.0
 	google.golang.org/protobuf v1.31.0
 )
@@ -14,9 +14,9 @@ require (
 	github.com/golang/protobuf v1.5.3 // indirect
 	github.com/google/go-cmp v0.6.0 // indirect
 	golang.org/x/exp v0.0.0-20230811145659-89c5cff77bcb // indirect
-	golang.org/x/net v0.17.0 // indirect
-	golang.org/x/sys v0.13.0 // indirect
-	golang.org/x/text v0.13.0 // indirect
-	google.golang.org/genproto v0.0.0-20231012201019-e917dd12ba7a // indirect
-	google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b // indirect
+	golang.org/x/net v0.19.0 // indirect
+	golang.org/x/sys v0.15.0 // indirect
+	golang.org/x/text v0.14.0 // indirect
+	google.golang.org/genproto v0.0.0-20231120223509-83a465c0220f // indirect
+	google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 // indirect
 )
```

### api/go.sum
```diff
@@ -10,19 +10,19 @@ github.com/google/go-cmp v0.6.0 h1:ofyhxvXcZhMsU5ulbFiLKl/XBFqE1GSq7atu8tAmTRI=
 github.com/google/go-cmp v0.6.0/go.mod h1:17dUlkBOakJ0+DkrSSNjCkIjxS6bF9zb3elmeNGIjoY=
 golang.org/x/exp v0.0.0-20230811145659-89c5cff77bcb h1:mIKbk8weKhSeLH2GmUTrvx8CjkyJmnU1wFmg59CUjFA=
 golang.org/x/exp v0.0.0-20230811145659-89c5cff77bcb/go.mod h1:FXUEEKJgO7OQYeo8N01OfiKP8RXMtf6e8aTskBGqWdc=
-golang.org/x/net v0.17.0 h1:pVaXccu2ozPjCXewfr1S7xza/zcXTity9cCdXQYSjIM=
-golang.org/x/net v0.17.0/go.mod h1:NxSsAGuq816PNPmqtQdLE42eU2Fs7NoRIZrHJAlaCOE=
-golang.org/x/sys v0.13.0 h1:Af8nKPmuFypiUBjVoU9V20FiaFXOcuZI21p0ycVYYGE=
-golang.org/x/sys v0.13.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/text v0.13.0 h1:ablQoSUd0tRdKxZewP80B+BaqeKJuVhuRxj/dkrun3k=
-golang.org/x/text v0.13.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
+golang.org/x/net v0.19.0 h1:zTwKpTd2XuCqf8huc7Fo2iSy+4RHPd10s4KzeTnVr1c=
+golang.org/x/net v0.19.0/go.mod h1:CfAk/cbD4CthTvqiEl8NpboMuiuOYsAr/7NOjZJtv1U=
+golang.org/x/sys v0.15.0 h1:h48lPFYpsTvQJZF4EKyI4aLHaev3CxivZmv7yZig9pc=
+golang.org/x/sys v0.15.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
+golang.org/x/text v0.14.0 h1:ScX5w1eTa3QqT8oi6+ziP7dTV1S2+ALU0bI+0zXKWiQ=
+golang.org/x/text v0.14.0/go.mod h1:18ZOQIKpY8NJVqYksKHtTdi31H5itFRjB5/qKTNYzSU=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
-google.golang.org/genproto v0.0.0-20231012201019-e917dd12ba7a h1:fwgW9j3vHirt4ObdHoYNwuO24BEZjSzbh+zPaNWoiY8=
-google.golang.org/genproto v0.0.0-20231012201019-e917dd12ba7a/go.mod h1:EMfReVxb80Dq1hhioy0sOsY9jCE46YDgHlJ7fWVUWRE=
-google.golang.org/genproto/googleapis/api v0.0.0-20231002182017-d307bd883b97 h1:W18sezcAYs+3tDZX4F80yctqa12jcP1PUS2gQu1zTPU=
-google.golang.org/genproto/googleapis/api v0.0.0-20231002182017-d307bd883b97/go.mod h1:iargEX0SFPm3xcfMI0d1domjg0ZF4Aa0p2awqyxhvF0=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b h1:ZlWIi1wSK56/8hn4QcBp/j9M7Gt3U/3hZw3mC7vDICo=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b/go.mod h1:swOH3j0KzcDDgGUWr+SNpyTen5YrXjS3eyPzFYKc6lc=
+google.golang.org/genproto v0.0.0-20231120223509-83a465c0220f h1:Vn+VyHU5guc9KjB5KrjI2q0wCOWEOIh0OEsleqakHJg=
+google.golang.org/genproto v0.0.0-20231120223509-83a465c0220f/go.mod h1:nWSwAFPb+qfNJXsoeO3Io7zf4tMSfN8EA8RlDA04GhY=
+google.golang.org/genproto/googleapis/api v0.0.0-20231106174013-bbf56f31fb17 h1:JpwMPBpFN3uKhdaekDpiNlImDdkUAyiJ6ez/uxGaUSo=
+google.golang.org/genproto/googleapis/api v0.0.0-20231106174013-bbf56f31fb17/go.mod h1:0xJLfVdJqpAPl8tDg1ujOCGzx6LFLttXT5NhllGOXY4=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 h1:DC7wcm+i+P1rN3Ff07vL+OndGg5OhNddHyTA+ocPqYE=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4/go.mod h1:eJVxU6o+4G1PSczBr85xmyvSNYAKvAYgkub40YGomFM=
 google.golang.org/grpc v1.59.0 h1:Z5Iec2pjwb+LEOqzpB2MR12/eKFhDPhuqW91O+4bwUk=
 google.golang.org/grpc v1.59.0/go.mod h1:aUPDwccQo6OTjy7Hct4AfBPD1GptF4fyUjIkQ9YtF98=
 google.golang.org/protobuf v1.26.0-rc.1/go.mod h1:jlhhOSvTdKEhbULTjvd4ARK9grFBp09yW+WbY/TyQbw=
```

### collections/go.mod
```diff
@@ -43,10 +43,10 @@ require (
 	github.com/spf13/cast v1.5.1 // indirect
 	github.com/syndtr/goleveldb v1.0.1-0.20220721030215-126854af5e6d // indirect
 	golang.org/x/exp v0.0.0-20230817173708-d852ddb80c63 // indirect
-	golang.org/x/net v0.17.0 // indirect
-	golang.org/x/sys v0.13.0 // indirect
-	golang.org/x/text v0.13.0 // indirect
-	google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b // indirect
+	golang.org/x/net v0.19.0 // indirect
+	golang.org/x/sys v0.15.0 // indirect
+	golang.org/x/text v0.14.0 // indirect
+	google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 // indirect
 	google.golang.org/grpc v1.59.0 // indirect
 	google.golang.org/protobuf v1.31.0 // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
```

### collections/go.sum
```diff
@@ -141,8 +141,8 @@ golang.org/x/net v0.0.0-20201021035429-f5854403a974/go.mod h1:sp8m0HH+o8qH0wwXwY
 golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT/9KSuxbyM7479/AVlXFRxuMCk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.17.0 h1:pVaXccu2ozPjCXewfr1S7xza/zcXTity9cCdXQYSjIM=
-golang.org/x/net v0.17.0/go.mod h1:NxSsAGuq816PNPmqtQdLE42eU2Fs7NoRIZrHJAlaCOE=
+golang.org/x/net v0.19.0 h1:zTwKpTd2XuCqf8huc7Fo2iSy+4RHPd10s4KzeTnVr1c=
+golang.org/x/net v0.19.0/go.mod h1:CfAk/cbD4CthTvqiEl8NpboMuiuOYsAr/7NOjZJtv1U=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190423024810-112230192c58/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190911185100-cd5d95a43a6e/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
@@ -166,16 +166,16 @@ golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220908164124-27713097b956/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.13.0 h1:Af8nKPmuFypiUBjVoU9V20FiaFXOcuZI21p0ycVYYGE=
-golang.org/x/sys v0.13.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.15.0 h1:h48lPFYpsTvQJZF4EKyI4aLHaev3CxivZmv7yZig9pc=
+golang.org/x/sys v0.15.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.13.0 h1:ablQoSUd0tRdKxZewP80B+BaqeKJuVhuRxj/dkrun3k=
-golang.org/x/text v0.13.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
+golang.org/x/text v0.14.0 h1:ScX5w1eTa3QqT8oi6+ziP7dTV1S2+ALU0bI+0zXKWiQ=
+golang.org/x/text v0.14.0/go.mod h1:18ZOQIKpY8NJVqYksKHtTdi31H5itFRjB5/qKTNYzSU=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20191119224855-298f0cb1881e/go.mod h1:b+2E5dAYhXwXZwtnZ6UAqBI28+e2cm9otk0dWdXHAEo=
 golang.org/x/tools v0.0.0-20200619180055-7c47624df98f/go.mod h1:EkVYQZoAsY45+roYkvgYkIh4xh/qjgUK9TdY2XT94GE=
@@ -186,8 +186,8 @@ golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8T
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20200804184101-5ec99f83aff1/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20220517211312-f3a8303e98df/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b h1:ZlWIi1wSK56/8hn4QcBp/j9M7Gt3U/3hZw3mC7vDICo=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b/go.mod h1:swOH3j0KzcDDgGUWr+SNpyTen5YrXjS3eyPzFYKc6lc=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 h1:DC7wcm+i+P1rN3Ff07vL+OndGg5OhNddHyTA+ocPqYE=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4/go.mod h1:eJVxU6o+4G1PSczBr85xmyvSNYAKvAYgkub40YGomFM=
 google.golang.org/grpc v1.59.0 h1:Z5Iec2pjwb+LEOqzpB2MR12/eKFhDPhuqW91O+4bwUk=
 google.golang.org/grpc v1.59.0/go.mod h1:aUPDwccQo6OTjy7Hct4AfBPD1GptF4fyUjIkQ9YtF98=
 google.golang.org/protobuf v0.0.0-20200109180630-ec00e32a8dfd/go.mod h1:DFci5gLYBciE7Vtevhsrf46CRTquxDuWsQurQQe4oz8=
```

### core/go.mod
```diff
@@ -46,11 +46,11 @@ require (
 	github.com/spf13/cast v1.5.1 // indirect
 	github.com/syndtr/goleveldb v1.0.1-0.20220721030215-126854af5e6d // indirect
 	golang.org/x/exp v0.0.0-20231006140011-7918f672742d // indirect
-	golang.org/x/net v0.17.0 // indirect
-	golang.org/x/sys v0.13.0 // indirect
-	golang.org/x/text v0.13.0 // indirect
-	google.golang.org/genproto v0.0.0-20231012201019-e917dd12ba7a // indirect
-	google.golang.org/genproto/googleapis/api v0.0.0-20231002182017-d307bd883b97 // indirect
-	google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b // indirect
+	golang.org/x/net v0.19.0 // indirect
+	golang.org/x/sys v0.15.0 // indirect
+	golang.org/x/text v0.14.0 // indirect
+	google.golang.org/genproto v0.0.0-20231120223509-83a465c0220f // indirect
+	google.golang.org/genproto/googleapis/api v0.0.0-20231106174013-bbf56f31fb17 // indirect
+	google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
 )
```

### core/go.sum
```diff
@@ -138,8 +138,8 @@ golang.org/x/net v0.0.0-20201021035429-f5854403a974/go.mod h1:sp8m0HH+o8qH0wwXwY
 golang.org/x/net v0.0.0-20210428140749-89ef3d95e781/go.mod h1:OJAsFXCWl8Ukc7SiCT/9KSuxbyM7479/AVlXFRxuMCk=
 golang.org/x/net v0.0.0-20220225172249-27dd8689420f/go.mod h1:CfG3xpIq0wQ8r1q4Su4UZFWDARRcnwPjda9FqA0JpMk=
 golang.org/x/net v0.0.0-20220607020251-c690dde0001d/go.mod h1:XRhObCWvk6IyKnWLug+ECip1KBveYUHfp+8e9klMJ9c=
-golang.org/x/net v0.17.0 h1:pVaXccu2ozPjCXewfr1S7xza/zcXTity9cCdXQYSjIM=
-golang.org/x/net v0.17.0/go.mod h1:NxSsAGuq816PNPmqtQdLE42eU2Fs7NoRIZrHJAlaCOE=
+golang.org/x/net v0.19.0 h1:zTwKpTd2XuCqf8huc7Fo2iSy+4RHPd10s4KzeTnVr1c=
+golang.org/x/net v0.19.0/go.mod h1:CfAk/cbD4CthTvqiEl8NpboMuiuOYsAr/7NOjZJtv1U=
 golang.org/x/sync v0.0.0-20180314180146-1d60e4601c6f/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190423024810-112230192c58/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
 golang.org/x/sync v0.0.0-20190911185100-cd5d95a43a6e/go.mod h1:RxMgew5VJxzue5/jJTE5uejpjVlOe/izrB70Jof72aM=
@@ -161,16 +161,16 @@ golang.org/x/sys v0.0.0-20210615035016-665e8c7367d1/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20211216021012-1d35b9e2eb4e/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220412211240-33da011f77ad/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220520151302-bc2c85ada10a/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.13.0 h1:Af8nKPmuFypiUBjVoU9V20FiaFXOcuZI21p0ycVYYGE=
-golang.org/x/sys v0.13.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.15.0 h1:h48lPFYpsTvQJZF4EKyI4aLHaev3CxivZmv7yZig9pc=
+golang.org/x/sys v0.15.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/term v0.0.0-20201126162022-7de9c90e9dd1/go.mod h1:bj7SfCRtBDWHUb9snDiAeCFNEtKQo2Wmx5Cou7ajbmo=
 golang.org/x/term v0.0.0-20210927222741-03fcf44c2211/go.mod h1:jbD1KX2456YbFQfuXm/mYQcufACuNUgVhRMnK/tPxf8=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.6/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
 golang.org/x/text v0.3.7/go.mod h1:u+2+/6zg+i71rQMx5EYifcz6MCKuco9NR6JIITiCfzQ=
-golang.org/x/text v0.13.0 h1:ablQoSUd0tRdKxZewP80B+BaqeKJuVhuRxj/dkrun3k=
-golang.org/x/text v0.13.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
+golang.org/x/text v0.14.0 h1:ScX5w1eTa3QqT8oi6+ziP7dTV1S2+ALU0bI+0zXKWiQ=
+golang.org/x/text v0.14.0/go.mod h1:18ZOQIKpY8NJVqYksKHtTdi31H5itFRjB5/qKTNYzSU=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20191119224855-298f0cb1881e/go.mod h1:b+2E5dAYhXwXZwtnZ6UAqBI28+e2cm9otk0dWdXHAEo=
 golang.org/x/tools v0.0.0-20200619180055-7c47624df98f/go.mod h1:EkVYQZoAsY45+roYkvgYkIh4xh/qjgUK9TdY2XT94GE=
@@ -181,12 +181,12 @@ golang.org/x/xerrors v0.0.0-20191011141410-1b5146add898/go.mod h1:I/5z698sn9Ka8T
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20200804184101-5ec99f83aff1/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
 golang.org/x/xerrors v0.0.0-20220517211312-f3a8303e98df/go.mod h1:K8+ghG5WaK9qNqU5K3HdILfMLy1f3aNYFI/wnl100a8=
-google.golang.org/genproto v0.0.0-20231012201019-e917dd12ba7a h1:fwgW9j3vHirt4ObdHoYNwuO24BEZjSzbh+zPaNWoiY8=
-google.golang.org/genproto v0.0.0-20231012201019-e917dd12ba7a/go.mod h1:EMfReVxb80Dq1hhioy0sOsY9jCE46YDgHlJ7fWVUWRE=
-google.golang.org/genproto/googleapis/api v0.0.0-20231002182017-d307bd883b97 h1:W18sezcAYs+3tDZX4F80yctqa12jcP1PUS2gQu1zTPU=
-google.golang.org/genproto/googleapis/api v0.0.0-20231002182017-d307bd883b97/go.mod h1:iargEX0SFPm3xcfMI0d1domjg0ZF4Aa0p2awqyxhvF0=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b h1:ZlWIi1wSK56/8hn4QcBp/j9M7Gt3U/3hZw3mC7vDICo=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b/go.mod h1:swOH3j0KzcDDgGUWr+SNpyTen5YrXjS3eyPzFYKc6lc=
+google.golang.org/genproto v0.0.0-20231120223509-83a465c0220f h1:Vn+VyHU5guc9KjB5KrjI2q0wCOWEOIh0OEsleqakHJg=
+google.golang.org/genproto v0.0.0-20231120223509-83a465c0220f/go.mod h1:nWSwAFPb+qfNJXsoeO3Io7zf4tMSfN8EA8RlDA04GhY=
+google.golang.org/genproto/googleapis/api v0.0.0-20231106174013-bbf56f31fb17 h1:JpwMPBpFN3uKhdaekDpiNlImDdkUAyiJ6ez/uxGaUSo=
+google.golang.org/genproto/googleapis/api v0.0.0-20231106174013-bbf56f31fb17/go.mod h1:0xJLfVdJqpAPl8tDg1ujOCGzx6LFLttXT5NhllGOXY4=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 h1:DC7wcm+i+P1rN3Ff07vL+OndGg5OhNddHyTA+ocPqYE=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4/go.mod h1:eJVxU6o+4G1PSczBr85xmyvSNYAKvAYgkub40YGomFM=
 google.golang.org/grpc v1.59.0 h1:Z5Iec2pjwb+LEOqzpB2MR12/eKFhDPhuqW91O+4bwUk=
 google.golang.org/grpc v1.59.0/go.mod h1:aUPDwccQo6OTjy7Hct4AfBPD1GptF4fyUjIkQ9YtF98=
 google.golang.org/protobuf v0.0.0-20200109180630-ec00e32a8dfd/go.mod h1:DFci5gLYBciE7Vtevhsrf46CRTquxDuWsQurQQe4oz8=
```

### depinject/go.mod
```diff
@@ -21,7 +21,7 @@ require (
 	github.com/pkg/errors v0.9.1 // indirect
 	github.com/pmezard/go-difflib v1.0.0 // indirect
 	github.com/rogpeppe/go-internal v1.11.0 // indirect
-	golang.org/x/sys v0.11.0 // indirect
-	golang.org/x/text v0.12.0 // indirect
+	golang.org/x/sys v0.15.0 // indirect
+	golang.org/x/text v0.14.0 // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
 )
```

### depinject/go.sum
```diff
@@ -50,12 +50,12 @@ golang.org/x/sync v0.0.0-20201020160332-67f06af15bc9/go.mod h1:RxMgew5VJxzue5/jJ
 golang.org/x/sys v0.0.0-20190215142949-d0b11bdaac8a/go.mod h1:STP8DvDyc/dI5b8T5hshtkjS+E42TnysNCUPdjciGhY=
 golang.org/x/sys v0.0.0-20190412213103-97732733099d/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
 golang.org/x/sys v0.0.0-20200930185726-fdedc70b468f/go.mod h1:h1NjWce9XRLGQEsW7wpKNCjG9DtNlClVuFLEZdDNbEs=
-golang.org/x/sys v0.11.0 h1:eG7RXZHdqOJ1i+0lgLgCpSXAp6M3LYlAo6osgSi0xOM=
-golang.org/x/sys v0.11.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.15.0 h1:h48lPFYpsTvQJZF4EKyI4aLHaev3CxivZmv7yZig9pc=
+golang.org/x/sys v0.15.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 golang.org/x/text v0.3.0/go.mod h1:NqM8EUOU14njkJ3fqMW+pc6Ldnwhi/IjpwHt7yyuwOQ=
 golang.org/x/text v0.3.3/go.mod h1:5Zoc/QRtKVWzQhOtBMvqHzDpF6irO9z98xDceosuGiQ=
-golang.org/x/text v0.12.0 h1:k+n5B8goJNdU7hSvEtMUz3d1Q6D/XW4COJSJR6fN0mc=
-golang.org/x/text v0.12.0/go.mod h1:TvPlkZtksWOMsz7fbANvkp4WM8x/WCo/om8BMLbz+aE=
+golang.org/x/text v0.14.0 h1:ScX5w1eTa3QqT8oi6+ziP7dTV1S2+ALU0bI+0zXKWiQ=
+golang.org/x/text v0.14.0/go.mod h1:18ZOQIKpY8NJVqYksKHtTdi31H5itFRjB5/qKTNYzSU=
 golang.org/x/tools v0.0.0-20180917221912-90fa682c2a6e/go.mod h1:n7NCudcB/nEzxVGmLbDWY5pfWTLqBcC2KZ6jyYvM4mQ=
 golang.org/x/tools v0.0.0-20191119224855-298f0cb1881e/go.mod h1:b+2E5dAYhXwXZwtnZ6UAqBI28+e2cm9otk0dWdXHAEo=
 golang.org/x/tools v0.0.0-20200619180055-7c47624df98f/go.mod h1:EkVYQZoAsY45+roYkvgYkIh4xh/qjgUK9TdY2XT94GE=
```

### errors/go.mod
```diff
@@ -14,8 +14,8 @@ require (
 	github.com/kr/pretty v0.3.0 // indirect
 	github.com/pmezard/go-difflib v1.0.0 // indirect
 	github.com/rogpeppe/go-internal v1.8.1 // indirect
-	golang.org/x/net v0.17.0 // indirect
-	google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b // indirect
+	golang.org/x/net v0.19.0 // indirect
+	google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 // indirect
 	google.golang.org/protobuf v1.31.0 // indirect
 	gopkg.in/check.v1 v1.0.0-20201130134442-10cb98267c6c // indirect
 	gopkg.in/yaml.v3 v3.0.1 // indirect
```

### errors/go.sum
```diff
@@ -24,13 +24,13 @@ github.com/rogpeppe/go-internal v1.8.1 h1:geMPLpDpQOgVyCg5z5GoRwLHepNdb71NXb67XF
 github.com/rogpeppe/go-internal v1.8.1/go.mod h1:JeRgkft04UBgHMgCIwADu4Pn6Mtm5d4nPKWu0nJ5d+o=
 github.com/stretchr/testify v1.8.4 h1:CcVxjf3Q8PM0mHUKJCdn+eZZtm5yQwehR5yeSVQQcUk=
 github.com/stretchr/testify v1.8.4/go.mod h1:sz/lmYIOXD/1dqDmKjjqLyZ2RngseejIcXlSw2iwfAo=
-golang.org/x/net v0.17.0 h1:pVaXccu2ozPjCXewfr1S7xza/zcXTity9cCdXQYSjIM=
-golang.org/x/net v0.17.0/go.mod h1:NxSsAGuq816PNPmqtQdLE42eU2Fs7NoRIZrHJAlaCOE=
-golang.org/x/sys v0.13.0 h1:Af8nKPmuFypiUBjVoU9V20FiaFXOcuZI21p0ycVYYGE=
-golang.org/x/text v0.13.0 h1:ablQoSUd0tRdKxZewP80B+BaqeKJuVhuRxj/dkrun3k=
+golang.org/x/net v0.19.0 h1:zTwKpTd2XuCqf8huc7Fo2iSy+4RHPd10s4KzeTnVr1c=
+golang.org/x/net v0.19.0/go.mod h1:CfAk/cbD4CthTvqiEl8NpboMuiuOYsAr/7NOjZJtv1U=
+golang.org/x/sys v0.15.0 h1:h48lPFYpsTvQJZF4EKyI4aLHaev3CxivZmv7yZig9pc=
+golang.org/x/text v0.14.0 h1:ScX5w1eTa3QqT8oi6+ziP7dTV1S2+ALU0bI+0zXKWiQ=
 golang.org/x/xerrors v0.0.0-20191204190536-9bdfabe68543/go.mod h1:I/5z698sn9Ka8TeJc9MKroUUfqBBauWjQqLJ2OPfmY0=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b h1:ZlWIi1wSK56/8hn4QcBp/j9M7Gt3U/3hZw3mC7vDICo=
-google.golang.org/genproto/googleapis/rpc v0.0.0-20231016165738-49dd2c1f3d0b/go.mod h1:swOH3j0KzcDDgGUWr+SNpyTen5YrXjS3eyPzFYKc6lc=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4 h1:DC7wcm+i+P1rN3Ff07vL+OndGg5OhNddHyTA+ocPqYE=
+google.golang.org/genproto/googleapis/rpc v0.0.0-20231127180814-3a041ad873d4/go.mod h1:eJVxU6o+4G1PSczBr85xmyvSNYAKvAYgkub40YGomFM=
 google.golang.org/grpc v1.59.0 h1:Z5Iec2pjwb+LEOqzpB2MR12/eKFhDPhuqW91O+4bwUk=
 google.golang.org/grpc v1.59.0/go.mod h1:aUPDwccQo6OTjy7Hct4AfBPD1GptF4fyUjIkQ9YtF98=
 google.golang.org/protobuf v1.26.0-rc.1/go.mod h1:jlhhOSvTdKEhbULTjvd4ARK9grFBp09yW+WbY/TyQbw=
```

### log/go.mod
```diff
@@ -12,5 +12,5 @@ require (
 	github.com/google/go-cmp v0.6.0 // indirect
 	github.com/mattn/go-colorable v0.1.13 // indirect
 	github.com/mattn/go-isatty v0.0.20 // indirect
-	golang.org/x/sys v0.13.0 // indirect
+	golang.org/x/sys v0.15.0 // indirect
 )
```

### log/go.sum
```diff
@@ -18,7 +18,7 @@ golang.org/x/sys v0.0.0-20210630005230-0f9fa26af87c/go.mod h1:oPkhp1MJrh7nUepCBc
 golang.org/x/sys v0.0.0-20210927094055-39ccf1dd6fa6/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.0.0-20220811171246-fbc7d0a398ab/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
 golang.org/x/sys v0.6.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
-golang.org/x/sys v0.13.0 h1:Af8nKPmuFypiUBjVoU9V20FiaFXOcuZI21p0ycVYYGE=
-golang.org/x/sys v0.13.0/go.mod h1:oPkhp1MJrh7nUepCBck5+mAzfO9JrbApNNgaTdGDITg=
+golang.org/x/sys v0.15.0 h1:h48lPFYpsTvQJZF4EKyI4aLHaev3CxivZmv7yZig9pc=
+golang.org/x/sys v0.15.0/go.mod h1:/VUhepiaJMQUp4+oa/7Zr1D23ma6VTLIYjOOTFZPUcA=
 gotest.tools/v3 v3.5.1 h1:EENdUnS3pdur5nybKYIh2Vfgc8IUNBjxDPSjtiJcOzU=
 gotest.tools/v3 v3.5.1/go.mod h1:isy3WKz7GK6uNw/sbHzfKBLvlvXwUyV06n6brMxxopU=
```
