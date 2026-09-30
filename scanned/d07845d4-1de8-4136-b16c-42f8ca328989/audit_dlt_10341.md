# [?] Upgrade Carmen - fix panic in Carmen forest (#78)

## Summary
Severity: Unknown
Chain: Sonic
Component: 0xsoniclabs/sonic
Published: 2023-12-14
Source: https://github.com/0xsoniclabs/sonic/commit/14c591034d68fa73bc350276a6788a7e4a9df67f
Type: security-commit

## Details
Upgrade Carmen - fix panic in Carmen forest (#78)

## Patch
### go.mod
```diff
@@ -44,7 +44,7 @@ require (
 )
 
 require (
-	github.com/Fantom-foundation/Carmen/go v0.0.0-20231212101609-250e8428217f
+	github.com/Fantom-foundation/Carmen/go v0.0.0-20231213175008-fd673a1fb1cd
 	github.com/Fantom-foundation/Tosca v0.0.0-20231211120117-160cf8af1fde
 )
 
```

### go.sum
```diff
@@ -57,8 +57,8 @@ github.com/CloudyKit/jet v2.1.3-0.20180809161101-62edd43e4f88+incompatible/go.mo
 github.com/DATA-DOG/go-sqlmock v1.3.3/go.mod h1:f/Ixk793poVmq4qj/V1dPUg2JEAKC73Q5eFN3EC/SaM=
 github.com/DataDog/zstd v1.4.5 h1:EndNeuB0l9syBZhut0wns3gV1hL8zX8LIu6ZiVHWLIQ=
 github.com/DataDog/zstd v1.4.5/go.mod h1:1jcaCB/ufaK+sKp1NBhlGmpz41jOoPQ35bpF36t7BBo=
-github.com/Fantom-foundation/Carmen/go v0.0.0-20231212101609-250e8428217f h1:NvIxG0dPI5S3TUAnBGGuf/sWcrjURFCbhkkMH+YYGGU=
-github.com/Fantom-foundation/Carmen/go v0.0.0-20231212101609-250e8428217f/go.mod h1:OwC6be3MyQBRWQeB1+qq1DovckBO2IjyB9DiYu4QLVU=
+github.com/Fantom-foundation/Carmen/go v0.0.0-20231213175008-fd673a1fb1cd h1:taPmHuW4loHaItwbHfpyYoh4kCA9CDJJqoTd/mN55K0=
+github.com/Fantom-foundation/Carmen/go v0.0.0-20231213175008-fd673a1fb1cd/go.mod h1:OwC6be3MyQBRWQeB1+qq1DovckBO2IjyB9DiYu4QLVU=
 github.com/Fantom-foundation/Tosca v0.0.0-20231211120117-160cf8af1fde h1:YxmvjNnYniFDmkh7A9xpiEz3wWVr5RcbP6zclrk/uU4=
 github.com/Fantom-foundation/Tosca v0.0.0-20231211120117-160cf8af1fde/go.mod h1:XfSNrGyRoCCpph5NeHriyuEh8wZw90w4mNH42vbFJ/g=
 github.com/Fantom-foundation/go-ethereum-substate v1.1.1-0.20231003122306-febfe681b4a7 h1:AWVp8bMwysTNE2/yORyxk4KF+isK9wFkPeLsT7SYS10=
```
