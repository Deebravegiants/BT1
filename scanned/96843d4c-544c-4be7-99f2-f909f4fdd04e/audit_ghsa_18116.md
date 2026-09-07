# [C] Pixar OpenUSD Sdf_PathNode Module Use-After-Free Vulnerability Leading to Potential Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-58p5-r2f6-g2cj
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:H (CVSS_V3)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-58p5-r2f6-g2cj
Type: github-advisory

## Affected
- PyPI: `usd-core` — affected >=0 <25.8

## Details
### Summary
A Use-After-Free (UAF) vulnerability has been discovered in the Sdf_PathNode module of the Pixar OpenUSD library. This issue occurs during the deletion of the Sdf_PrimPathNode object in multi-threaded environments, where freed memory is accessed. This results in segmentation faults or bus errors, allowing attackers to potentially exploit the vulnerability for remote code execution (RCE). By using a specially crafted .usd file, an attacker could gain control of the affected system. The vulnerability has been confirmed in multiple OpenUSD tools, including sdfdump, usdtree, usdcat, and sdffilter.

### Patches

This is fixed with [commit 0d74f31](https://github.com/PixarAnimationStudios/OpenUSD/commit/0d74f31fe64310791e274e587c9926335e9db9db), with the fix available in OpenUSD 25.08 and onwards.

### Details
The issue is a Use-After-Free vulnerability in the Sdf_PathNode destruction process, specifically in Sdf_PrimPathNode::~Sdf_PrimPathNode(). When multiple threads attempt to destroy or modify the same Sdf_PathNode object, a race condition can occur, causing the object to be accessed after it has been freed. This leads to segmentation faults or bus errors, as observed in the crash logs.
```
root@DESKTOP-7VTO277:/mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/bin# ./sdffilter /mnt/c/Users/HomePc/Downloads/one.usd
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'extent' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'extent' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
AddressSanitizer:DEADLYSIGNAL
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'extent' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
=================================================================
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexCounts' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
AddressSanitizerWarning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexCounts' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
:DEADLYSIGNAL
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Standin' to path '/HumanFemale_Group/KidThinButtonDown/Geom/LSock/Hair/Body/HeelSeam_sbdv/BrowL_HairLayer.primvars:displayColor'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexIndices' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Tongue_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Body/Body_sbdv.points'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexIndices' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Geom' to path '/HumanFemale_Group/KidThinButtonDown/Geom/LSock/Hair/Body/HeelSeam_sbdv.faceVertexCounts'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'points' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Cornea_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Body/Body_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:displayColor' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Iris_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Body/Body_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'extent' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:geomBindTransform' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexCounts' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointIndices' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexIndices' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
==270474==ERROR: AddressSanitizer: SEGV on unknown address 0x7f8500000008 (pc 0x7f855a574b2b bp 0x7ffcd379aa30 sp 0x7ffcd379a770 T0)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Pupil_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Body/Body_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'points' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexCounts' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:displayColor' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Sclera_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Body/Body_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:geomBindTransform' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointIndices' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
==270474==The signal is caused by a WRITE memory access.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointWeights' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'points' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexIndices' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointWeights' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'points' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'subdivisionScheme' to a prim path (/HumanFemale_Group/HumanFemaleHair.xformOpOrder)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:displayColor' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:displayColor' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'subdivisionScheme' to a prim path (/HumanFemale_Group/SocksHuman.xformOp:transform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:geomBindTransform' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointIndices' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointIndices' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointWeights' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointWeights' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'visibility' to a prim path (/RShoe/Body/ShoeBody_sbdv/Geom/RShoe/Sole/Standin/Shell_sbdv.interpolateBoundary)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'subdivisionScheme' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=faceBones}Geom/Face/Eyes/LEye/Pupil_sbdv/LEye/Iris_sbdv.faceVertexCounts)
AddressSanitizer:DEADLYSIGNAL
    #0 0x7f855a574b2b in std::__atomic_base<unsigned int>::fetch_add(unsigned int, std::memory_order) /usr/include/c++/11/bits/atomic_base.h:618
    #1 0x7f855a574b2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountIncrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:742
    #2 0x7f855a574b2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::_IncrementIfValid() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:247
    #3 0x7f855a574b2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::TfDelegatedCountPtr(pxrInternal_v0_24__pxrReserved__::TfDelegatedCountIncrementTagType, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:116
    #4 0x7f855a574b2b in pxrInternal_v0_24__pxrReserved__::Sdf_PrimPathNode::~Sdf_PrimPathNode() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:752
    #5 0x5653213d7c80 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::_Destroy() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:659
    #6 0x5653213d7c80 in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountDecrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:746
    #7 0x5653213d7c80 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::_DecRef() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:177
    #8 0x5653213d7c80 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::~Sdf_PathNodeHandleImpl() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:97
AddressSanitizer:DEADLYSIGNAL
AddressSanitizer: nested bug in the same thread, aborting.
```

```
root@DESKTOP-7VTO277:/mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/bin# ./usdcat /mnt/c/Users/HomePc/Downloads/one.usd
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'LEye' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Eyes_REye_Lids_OutCornerUD.xformOp:transform'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'xformOp:transform' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Mouth_JawUD/Geom/Face/Eyes/LEye/Sclera_sbdv.primvars:skel:jointIndices)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Cornea_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/HeelSeam_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'xformOpOrder' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Mouth_JawUD/Geom/Face/Eyes/LEye/Sclera_sbdv.primvars:skel:jointIndices)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Iris_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/HeelSeam_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Pupil_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/HeelSeam_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'HeelSeam_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/ShoeBody_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'xformOp:transform' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Mouth_JawUD/Geom/Face/Eyes/LEye/Pupil_sbdv.subdivisionScheme)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Geom' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Mouth_JawUD/Geom/Face/Eyes/LEye/Sclera_sbdv.primvars:skel:jointIndices'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'xformOpOrder' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Mouth_JawUD/Geom/Face/Eyes/LEye/Pupil_sbdv.subdivisionScheme)
AddressSanitizer:DEADLYSIGNAL
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointIndices' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/ShoeBody_sbdv.primvars:skel:jointWeights)
=================================================================
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'ShoeBody_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/ShoeBody_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Tongue_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=reduced}Geom/Face/Body_sbdv.primvars:skel:jointIndices'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'doubleSided' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointWeights' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/ShoeBody_sbdv.primvars:skel:jointWeights)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Sclera_sbdv' to path '/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=faceBones}Geom/Hair/Layers/Geom/LShoe/Body/HeelSeam_sbdv.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Geom' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Mouth_JawUD/Geom/Face/Eyes/LEye/Pupil_sbdv.subdivisionScheme'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'REye' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Eyes_REye_Lids_OutCornerUD.xformOp:transform'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'extent' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexCounts' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexIndices' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'points' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:displayColor' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
==271750==ERROR: AddressSanitizer: SEGV on unknown address 0x7f9602c0040f (pc 0x7f962b94286f bp 0x7f96233abb40 sp 0x7f96233abaf0 T10)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:geomBindTransform' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'subdivisionScheme' to a prim path (/HumanFemale_Group/HumanFemale{rigComplexity=}{rigComplexity=high}Geom/Hair/Layers/Geom/LShoe/BrowL_HairLayer/Body/ShoeBody_sbdv.faceVertexCounts)
==271750==The signal is caused by a READ memory access.
    #0 0x7f962b94286f in _WriteTextToBuffer<pxrInternal_v0_24__pxrReserved__::(anonymous namespace)::_StringBuffer> /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:662
    #1 0x7f962b942d6f in pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::_CreatePathToken(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:620
    #2 0x7f962b945eb3 in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:506
    #3 0x7f962b945eb3 in FindOrCreate<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::GetPathToken(const pxrInternal_v0_24__pxrReserved__::Sdf_PathNode*, const pxrInternal_v0_24__pxrReserved__::Sdf_PathNode*)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:458
    #4 0x7f962b945eb3 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::GetPathToken(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:504
    #5 0x7f962b852a5c in pxrInternal_v0_24__pxrReserved__::SdfPath::GetToken() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp:339
    #6 0x7f962b852d2c in pxrInternal_v0_24__pxrReserved__::SdfPath::GetText() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp:353
    #7 0x7f962b868bd7 in pxrInternal_v0_24__pxrReserved__::SdfPath::AppendChild(pxrInternal_v0_24__pxrReserved__::TfToken const&) const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp:824
    #8 0x7f962b8708b6 in pxrInternal_v0_24__pxrReserved__::SdfPath::AppendElementToken(pxrInternal_v0_24__pxrReserved__::TfToken const&) const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp:1166
    #9 0x7f962ca352e5 in pxrInternal_v0_24__pxrReserved__::Usd_CrateFile::CrateFile::_BuildDecompressedPathsImpl(std::vector<unsigned int, std::allocator<unsigned int> > const&, std::vector<int, std::allocator<int> > const&, std::vector<int, std::allocator<int> > const&, unsigned long, pxrInternal_v0_24__pxrReserved__::SdfPath, pxrInternal_v0_24__pxrReserved__::WorkDispatcher&) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/usd/crateFile.cpp:3741
    #10 0x7f962ca3d435 in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/usd/crateFile.cpp:3775
    #11 0x7f962ca3d435 in execute /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/work/dispatcher.h:170
    #12 0x7f9629c0f135 in tbb::internal::custom_scheduler<tbb::internal::IntelSchedulerTraits>::process_bypass_loop(tbb::internal::context_guard_helper<false>&, tbb::task*, long) ../../src/tbb/custom_scheduler.h:474
    #13 0x7f9629c1026c in tbb::internal::custom_scheduler<tbb::internal::IntelSchedulerTraits>::local_wait_for_all(tbb::task&, tbb::task*) ../../src/tbb/custom_scheduler.h:636
    #14 0x7f9629bfa5d3 in tbb::internal::arena::process(tbb::internal::generic_scheduler&) ../../src/tbb/arena.cpp:196
    #15 0x7f9629bf1741 in tbb::internal::market::process(rml::job&) ../../src/tbb/market.cpp:667
    #16 0x7f9629be3889 in tbb::internal::rml::private_worker::run() ../../src/tbb/private_server.cpp:266
    #17 0x7f9629be472a in tbb::internal::rml::private_worker::thread_routine(void*) ../../src/tbb/private_server.cpp:219
    #18 0x7f96296c4ac2 in start_thread nptl/pthread_create.c:442
    #19 0x7f962975684f  (/lib/x86_64-linux-gnu/libc.so.6+0x12684f)

AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: SEGV /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:662 in _WriteTextToBuffer<pxrInternal_v0_24__pxrReserved__::(anonymous namespace)::_StringBuffer>
Thread T10 created by T3 here:
    #0 0x7f962e987685 in __interceptor_pthread_create ../../../../src/libsanitizer/asan/asan_interceptors.cpp:216
    #1 0x7f9629be4ff1 in rml::internal::thread_monitor::launch(void* (*)(void*), void*, unsigned long) ../../src/tbb/../rml/server/thread_monitor.h:218
    #2 0x7f9629be4ff1 in tbb::internal::rml::private_worker::wake_or_launch() ../../src/tbb/private_server.cpp:297
    #3 0x7f9629be3303 in tbb::internal::rml::private_server::wake_some(int) ../../src/tbb/private_server.cpp:395
    #4 0x7f9629be3722 in tbb::internal::rml::private_server::propagate_chain_reaction() ../../src/tbb/private_server.cpp:157
    #5 0x7f9629be3722 in tbb::internal::rml::private_worker::run() ../../src/tbb/private_server.cpp:257
    #6 0x7f9629be472a in tbb::internal::rml::private_worker::thread_routine(void*) ../../src/tbb/private_server.cpp:219
    #7 0x7f96296c4ac2 in start_thread nptl/pthread_create.c:442

Thread T3 created by T1 here:
    #0 0x7f962e987685 in __interceptor_pthread_create ../../../../src/libsanitizer/asan/asan_interceptors.cpp:216
    #1 0x7f9629be4ff1 in rml::internal::thread_monitor::launch(void* (*)(void*), void*, unsigned long) ../../src/tbb/../rml/server/thread_monitor.h:218
    #2 0x7f9629be4ff1 in tbb::internal::rml::private_worker::wake_or_launch() ../../src/tbb/private_server.cpp:297
    #3 0x7f9629be3303 in tbb::internal::rml::private_server::wake_some(int) ../../src/tbb/private_server.cpp:395
    #4 0x7f9629be3722 in tbb::internal::rml::private_server::propagate_chain_reaction() ../../src/tbb/private_server.cpp:157
    #5 0x7f9629be3722 in tbb::internal::rml::private_worker::run() ../../src/tbb/private_server.cpp:257
    #6 0x7f9629be472a in tbb::internal::rml::private_worker::thread_routine(void*) ../../src/tbb/private_server.cpp:219
    #7 0x7f96296c4ac2 in start_thread nptl/pthread_create.c:442

Thread T1 created by T0 here:
    #0 0x7f962e987685 in __interceptor_pthread_create ../../../../src/libsanitizer/asan/asan_interceptors.cpp:216
    #1 0x7f9629be4ff1 in rml::internal::thread_monitor::launch(void* (*)(void*), void*, unsigned long) ../../src/tbb/../rml/server/thread_monitor.h:218
    #2 0x7f9629be4ff1 in tbb::internal::rml::private_worker::wake_or_launch() ../../src/tbb/private_server.cpp:297
    #3 0x7f9629be3303 in tbb::internal::rml::private_server::wake_some(int) ../../src/tbb/private_server.cpp:395
    #4 0x7f9629be3479 in tbb::internal::rml::private_server::adjust_job_count_estimate(int) ../../src/tbb/private_server.cpp:406
    #5 0x7f9629bf4f27 in tbb::internal::market::adjust_demand(tbb::internal::arena&, int) ../../src/tbb/market.cpp:655
    #6 0x7f9629c0d7e0 in void tbb::internal::arena::advertise_new_work<(tbb::internal::arena::new_work_type)0>() ../../src/tbb/arena.h:548
    #7 0x7f9629c096e8 in tbb::internal::generic_scheduler::local_spawn(tbb::task*, tbb::task*&) ../../src/tbb/scheduler.cpp:716
    #8 0x7f9629c09e36 in tbb::internal::generic_scheduler::spawn(tbb::task&, tbb::task*&) ../../src/tbb/scheduler.cpp:742
    #9 0x7f962a56553b in tbb::interface5::internal::task_base::spawn(tbb::task&) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task.h:1125
    #10 0x7f962a56553b in Run<const pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(const std::vector<std::__cxx11::basic_string<char> >&, bool, const AddVisitedPathCallback&, const AddPluginCallback&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*)::<lambda()>&> /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/work/dispatcher.h:99
    #11 0x7f962a56553b in Run<pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(const std::vector<std::__cxx11::basic_string<char> >&, bool, const AddVisitedPathCallback&, const AddPluginCallback&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/info.cpp:462
    #12 0x7f962a56553b in Run<pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(const std::vector<std::__cxx11::basic_string<char> >&, bool, const AddVisitedPathCallback&, const AddPluginCallback&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/info.cpp:495
    #13 0x7f962a56553b in pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, bool, std::function<bool (std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)> const&, std::function<void (pxrInternal_v0_24__pxrReserved__::Plug_RegistrationMetadata const&)> const&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/info.cpp:716
    #14 0x7f962a6052a6 in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/registry.cpp:125
    #15 0x7f962a6052a6 in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task_arena.h:96
    #16 0x7f9629bf7d38 in tbb::interface7::internal::isolate_within_arena(tbb::interface7::internal::delegate_base&, long) ../../src/tbb/arena.cpp:1199
    #17 0x7f962a606cb3 in isolate_impl<void, const pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(const std::vector<std::__cxx11::basic_string<char> >&, bool)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task_arena.h:216
    #18 0x7f962a606cb3 in isolate<pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(const std::vector<std::__cxx11::basic_string<char> >&, bool)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task_arena.h:472
    #19 0x7f962a606cb3 in WorkWithScopedParallelism<pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(const std::vector<std::__cxx11::basic_string<char> >&, bool)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/work/withScopedParallelism.h:106
    #20 0x7f962a606cb3 in pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, bool) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/registry.cpp:124
    #21 0x7f962a60d09d in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/registry.cpp:281
    #22 0x7f962a60d09d in __invoke_impl<void, pxrInternal_v0_24__pxrReserved__::PlugPlugin::_RegisterAllPlugins()::<lambda()> > /usr/include/c++/11/bits/invoke.h:61
    #23 0x7f962a60d09d in __invoke<pxrInternal_v0_24__pxrReserved__::PlugPlugin::_RegisterAllPlugins()::<lambda()> > /usr/include/c++/11/bits/invoke.h:96
    #24 0x7f962a60d09d in operator() /usr/include/c++/11/mutex:776
    #25 0x7f962a60d09d in operator() /usr/include/c++/11/mutex:712
    #26 0x7f962a60d09d in _FUN /usr/include/c++/11/mutex:712
    #27 0x7f96296c9ee7 in __pthread_once_slow nptl/pthread_once.c:116

==271750==ABORTING
```

```
root@DESKTOP-7VTO277:/mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/bin# ./sdfdump  /mnt/c/Users/HomePc/Downloads/one.usd
AddressSanitizerAddressSanitizer:DEADLYSIGNAL
=================================================================
:DEADLYSIGNAL
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Hair' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Pupil_sbdv/ThumbToeNail_sbdv.primvars:skel:jointIndices'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Render' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Pupil_sbdv/ThumbToeNail_sbdv.primvars:skel:jointIndices'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Standin' to path '/HumanFemale_Group/SocksHuman/Geom/RSock/AnkleSock_sbdv.primvars:displayColor'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'ButtonDownRenderMesh_sbdv' to path '/.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Geom' to path '/HumanFemale_Group/KidThinButtonDown/Face{rigComplexity=}RShoe/Body/HeelSeam_sbdv.extent'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Render' to path '/HumanFemale_Group/KidThinButtonDown/Face{rigComplexity=}RShoe/Sole/REye.subdivisionScheme'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Iris_sbdv' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Cheeks_LCheek_Puff.primvars:skel:geomBindTransform'.
AddressSanitizer:DEADLYSIGNAL
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'extent' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Pupil_sbdv' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Cheeks_LCheek_Puff.primvars:skel:geomBindTransform'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Standin' to path '/HumanFemale_Group/HumanFemale{rigComplexity=reduced}HeadHair/BetaRight_HairLayer/Standin/Shell_sbdv/Iris_sbdv.points'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexCounts' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Sclera_sbdv' to path '/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Body/Body_sbdv/HumanFemale_Anim_Face_Cheeks_LCheek_Puff.primvars:skel:geomBindTransform'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexIndices' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
==271764==ERROR: AddressSanitizer: SEGV on unknown address 0x7fb401c00409 (pc 0x7fb48c37eb2b bp 0x7fb4851b1930 sp 0x7fb4851b1670 T5)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'points' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:displayColor' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointIndices' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Body_sbdv' to path '/HumanFemale_Group/KidThinButtonDown{rigComplexity=}Body/Render/ShoeBody_sbdv.faceVertexCounts'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointWeights' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
==271764==The signal is caused by a WRITE memory access.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'visibility' to a prim path (/HumanFemale_Group/HumanFemale/Geom/Body/Nails/RFingerNails/Iris_sbdv/Geom/Face/Eyes/REye/Cornea_sbdv.primvars:skel:jointWeights)
    #0 0x7fb48c37eb2b in std::__atomic_base<unsigned int>::fetch_add(unsigned int, std::memory_order) /usr/include/c++/11/bits/atomic_base.h:618
    #1 0x7fb48c37eb2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountIncrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:742
    #2 0x7fb48c37eb2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::_IncrementIfValid() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:247
    #3 0x7fb48c37eb2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::TfDelegatedCountPtr(pxrInternal_v0_24__pxrReserved__::TfDelegatedCountIncrementTagType, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:116
    #4 0x7fb48c37eb2b in pxrInternal_v0_24__pxrReserved__::Sdf_PrimPathNode::~Sdf_PrimPathNode() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:752
    #5 0x7fb48c2b1327 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::_Destroy() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:659
    #6 0x7fb48c2b1327 in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountDecrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:746
    #7 0x7fb48c37f484 in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::_DecrementIfValid() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:253
    #8 0x7fb48c37f484 in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::~TfDelegatedCountPtr() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:192
    #9 0x7fb48c37f484 in pxrInternal_v0_24__pxrReserved__::Sdf_PrimPathNode::~Sdf_PrimPathNode() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:752
    #10 0x7fb48c2b1327 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::_Destroy() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:659
    #11 0x7fb48c2b1327 in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountDecrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:746
    #12 0x7fb48c37f4e0 in pxrInternal_v0_24__pxrReserved__::Sdf_PrimPartPathNode::~Sdf_PrimPartPathNode() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:324
    #13 0x7fb48c37f4e0 in pxrInternal_v0_24__pxrReserved__::Sdf_PrimPathNode::~Sdf_PrimPathNode() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:755
    #14 0x556821bbf7c0 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::_Destroy() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:659
    #15 0x556821bbf7c0 in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountDecrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:746
    #16 0x556821bbf7c0 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::_DecRef() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:177
    #17 0x556821bbf7c0 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::~Sdf_PathNodeHandleImpl() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:97
    #18 0x7fb4821c1463 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::operator=(pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>&&) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:117
    #19 0x7fb4821c1463 in pxrInternal_v0_24__pxrReserved__::SdfPath::operator=(pxrInternal_v0_24__pxrReserved__::SdfPath&&) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:273
    #20 0x7fb4821c1463 in pxrInternal_v0_24__pxrReserved__::Usd_CrateFile::CrateFile::_BuildDecompressedPathsImpl(std::vector<unsigned int, std::allocator<unsigned int> > const&, std::vector<int, std::allocator<int> > const&, std::vector<int, std::allocator<int> > const&, unsigned long, pxrInternal_v0_24__pxrReserved__::SdfPath, pxrInternal_v0_24__pxrReserved__::WorkDispatcher&) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/usd/crateFile.cpp:3743
    #21 0x7fb4821c9435 in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/usd/crateFile.cpp:3775
    #22 0x7fb4821c9435 in execute /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/work/dispatcher.h:170
    #23 0x7fb48a639135 in tbb::internal::custom_scheduler<tbb::internal::IntelSchedulerTraits>::process_bypass_loop(tbb::internal::context_guard_helper<false>&, tbb::task*, long) ../../src/tbb/custom_scheduler.h:474
    #24 0x7fb48a63a26c in tbb::internal::custom_scheduler<tbb::internal::IntelSchedulerTraits>::local_wait_for_all(tbb::task&, tbb::task*) ../../src/tbb/custom_scheduler.h:636
    #25 0x7fb48a6245d3 in tbb::internal::arena::process(tbb::internal::generic_scheduler&) ../../src/tbb/arena.cpp:196
    #26 0x7fb48a61b741 in tbb::internal::market::process(rml::job&) ../../src/tbb/market.cpp:667
    #27 0x7fb48a60d889 in tbb::internal::rml::private_worker::run() ../../src/tbb/private_server.cpp:266
    #28 0x7fb48a60e72a in tbb::internal::rml::private_worker::thread_routine(void*) ../../src/tbb/private_server.cpp:219
    #29 0x7fb48a0ecac2 in start_thread nptl/pthread_create.c:442
    #30 0x7fb48a17e84f  (/lib/x86_64-linux-gnu/libc.so.6+0x12684f)

AddressSanitizer can not provide additional info.
SUMMARY: AddressSanitizer: SEGV /usr/include/c++/11/bits/atomic_base.h:618 in std::__atomic_base<unsigned int>::fetch_add(unsigned int, std::memory_order)
Thread T5 created by T1 here:
    #0 0x7fb48c91e685 in __interceptor_pthread_create ../../../../src/libsanitizer/asan/asan_interceptors.cpp:216
    #1 0x7fb48a60eff1 in rml::internal::thread_monitor::launch(void* (*)(void*), void*, unsigned long) ../../src/tbb/../rml/server/thread_monitor.h:218
    #2 0x7fb48a60eff1 in tbb::internal::rml::private_worker::wake_or_launch() ../../src/tbb/private_server.cpp:297
    #3 0x7fb48a60d303 in tbb::internal::rml::private_server::wake_some(int) ../../src/tbb/private_server.cpp:395
    #4 0x7fb48a60d722 in tbb::internal::rml::private_server::propagate_chain_reaction() ../../src/tbb/private_server.cpp:157
    #5 0x7fb48a60d722 in tbb::internal::rml::private_worker::run() ../../src/tbb/private_server.cpp:257
    #6 0x7fb48a60e72a in tbb::internal::rml::private_worker::thread_routine(void*) ../../src/tbb/private_server.cpp:219
    #7 0x7fb48a0ecac2 in start_thread nptl/pthread_create.c:442

Thread T1 created by T0 here:
    #0 0x7fb48c91e685 in __interceptor_pthread_create ../../../../src/libsanitizer/asan/asan_interceptors.cpp:216
    #1 0x7fb48a60eff1 in rml::internal::thread_monitor::launch(void* (*)(void*), void*, unsigned long) ../../src/tbb/../rml/server/thread_monitor.h:218
    #2 0x7fb48a60eff1 in tbb::internal::rml::private_worker::wake_or_launch() ../../src/tbb/private_server.cpp:297
    #3 0x7fb48a60d303 in tbb::internal::rml::private_server::wake_some(int) ../../src/tbb/private_server.cpp:395
    #4 0x7fb48a60d479 in tbb::internal::rml::private_server::adjust_job_count_estimate(int) ../../src/tbb/private_server.cpp:406
    #5 0x7fb48a61ef27 in tbb::internal::market::adjust_demand(tbb::internal::arena&, int) ../../src/tbb/market.cpp:655
    #6 0x7fb48a6377e0 in void tbb::internal::arena::advertise_new_work<(tbb::internal::arena::new_work_type)0>() ../../src/tbb/arena.h:548
    #7 0x7fb48a6336e8 in tbb::internal::generic_scheduler::local_spawn(tbb::task*, tbb::task*&) ../../src/tbb/scheduler.cpp:716
    #8 0x7fb48a633e36 in tbb::internal::generic_scheduler::spawn(tbb::task&, tbb::task*&) ../../src/tbb/scheduler.cpp:742
    #9 0x7fb48b4ac53b in tbb::interface5::internal::task_base::spawn(tbb::task&) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task.h:1125
    #10 0x7fb48b4ac53b in Run<const pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(const std::vector<std::__cxx11::basic_string<char> >&, bool, const AddVisitedPathCallback&, const AddPluginCallback&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*)::<lambda()>&> /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/work/dispatcher.h:99
    #11 0x7fb48b4ac53b in Run<pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(const std::vector<std::__cxx11::basic_string<char> >&, bool, const AddVisitedPathCallback&, const AddPluginCallback&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/info.cpp:462
    #12 0x7fb48b4ac53b in Run<pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(const std::vector<std::__cxx11::basic_string<char> >&, bool, const AddVisitedPathCallback&, const AddPluginCallback&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/info.cpp:495
    #13 0x7fb48b4ac53b in pxrInternal_v0_24__pxrReserved__::Plug_ReadPlugInfo(std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, bool, std::function<bool (std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const&)> const&, std::function<void (pxrInternal_v0_24__pxrReserved__::Plug_RegistrationMetadata const&)> const&, pxrInternal_v0_24__pxrReserved__::Plug_TaskArena*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/info.cpp:716
    #14 0x7fb48b54c2a6 in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/registry.cpp:125
    #15 0x7fb48b54c2a6 in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task_arena.h:96
    #16 0x7fb48a621d38 in tbb::interface7::internal::isolate_within_arena(tbb::interface7::internal::delegate_base&, long) ../../src/tbb/arena.cpp:1199
    #17 0x7fb48b54dcb3 in isolate_impl<void, const pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(const std::vector<std::__cxx11::basic_string<char> >&, bool)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task_arena.h:216
    #18 0x7fb48b54dcb3 in isolate<pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(const std::vector<std::__cxx11::basic_string<char> >&, bool)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/include/tbb/task_arena.h:472
    #19 0x7fb48b54dcb3 in WorkWithScopedParallelism<pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(const std::vector<std::__cxx11::basic_string<char> >&, bool)::<lambda()> > /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/work/withScopedParallelism.h:106
    #20 0x7fb48b54dcb3 in pxrInternal_v0_24__pxrReserved__::PlugRegistry::_RegisterPlugins(std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, bool) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/registry.cpp:124
    #21 0x7fb48b55409d in operator() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/plug/registry.cpp:281
    #22 0x7fb48b55409d in __invoke_impl<void, pxrInternal_v0_24__pxrReserved__::PlugPlugin::_RegisterAllPlugins()::<lambda()> > /usr/include/c++/11/bits/invoke.h:61
    #23 0x7fb48b55409d in __invoke<pxrInternal_v0_24__pxrReserved__::PlugPlugin::_RegisterAllPlugins()::<lambda()> > /usr/include/c++/11/bits/invoke.h:96
    #24 0x7fb48b55409d in operator() /usr/include/c++/11/mutex:776
    #25 0x7fb48b55409d in operator() /usr/include/c++/11/mutex:712
    #26 0x7fb48b55409d in _FUN /usr/include/c++/11/mutex:712
    #27 0x7fb48a0f1ee7 in __pthread_once_slow nptl/pthread_once.c:116

==271764==ABORTING
```

```
root@DESKTOP-7VTO277:/mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/asan_install/bin# ./usdtree /mnt/c/Users/HomePc/Downloads/one.usd
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'LFingerNails' to path '/HumanFemale_Group/HumanFemale/Geom/Face/Geom/Hair/Layers/EyeHair/BrowL_HairLayer/Standin/Shell_sbdv.extent'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'LToeNails' to path '/HumanFemale_Group/HumanFemale/Geom/Face/Geom/Hair/Layers/EyeHair/BrowL_HairLayer/Standin/Shell_sbdv.extent'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Hair' to path '/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.faceVertexIndices'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Standin' to path '/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.faceVertexIndices'.
AddressSanitizerAddressSanitizer:DEADLYSIGNAL
:DEADLYSIGNAL
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Geom' to path '/HumanFemale_Group/KidThinLeggings/LEye/Iris_sbdv/BetaRight_HairLayer/Standin/Shell_sbdv.extent'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'RFingerNails' to path '/HumanFemale_Group/HumanFemale/Geom/Face/Geom/Hair/Layers/EyeHair/BrowL_HairLayer/Standin/Shell_sbdv.extent'.
=================================================================
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'BrowL_HairLayer' to path '/EyeHair/Standin.extent'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'RToeNails' to path '/HumanFemale_Group/HumanFemale/Geom/Face/Geom/Hair/Layers/EyeHair/BrowL_HairLayer/Standin/Shell_sbdv.extent'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Render' to path '/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.xformOpOrder'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Body' to path '/HumanFemale_Group/KidThinLeggings/Geom.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'extent' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Sole' to path '/HumanFemale_Group/KidThinLeggings/Geom.primvars:skel:jointWeights'.
Warning (secondary thread): in AppendChild at line 824 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Cannot append child 'Geom' to path '/HumanFemale_Group/KidThinLeggings/Geom/Render/ButtonDownRenderMesh_sbdv/RShoe/HeelSeam_sbdv/ShoeBody_sbdv.primvars:skel:jointIndices'.
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexCounts' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'faceVertexIndices' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'points' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:displayColor' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
AddressSanitizerWarning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:geomBindTransform' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
:DEADLYSIGNAL
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointIndices' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
AddressSanitizer:DEADLYSIGNAL
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'primvars:skel:jointWeights' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
Warning (secondary thread): in AppendProperty at line 921 of /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.cpp -- Can only append a property 'subdivisionScheme' to a prim path (/HumanFemale_Group/KidThinLeggings/LEye/Sclera_sbdv.primvars:skel:geomBindTransform)
==271780==ERROR: AddressSanitizer: SEGV on unknown address 0x7fea02800109 (pc 0x7fea78e0db2b bp 0x7ffe818d03e0 sp 0x7ffe818d0120 T0)
==271780==The signal is caused by a WRITE memory access.
    #0 0x7fea78e0db2b in std::__atomic_base<unsigned int>::fetch_add(unsigned int, std::memory_order) /usr/include/c++/11/bits/atomic_base.h:618
    #1 0x7fea78e0db2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountIncrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:742
    #2 0x7fea78e0db2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::_IncrementIfValid() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:247
    #3 0x7fea78e0db2b in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountPtr<pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::TfDelegatedCountPtr(pxrInternal_v0_24__pxrReserved__::TfDelegatedCountIncrementTagType, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/base/tf/delegatedCountPtr.h:116
    #4 0x7fea78e0db2b in pxrInternal_v0_24__pxrReserved__::Sdf_PrimPathNode::~Sdf_PrimPathNode() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.cpp:752
    #5 0x564aa248fd20 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNode::_Destroy() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:659
    #6 0x564aa248fd20 in pxrInternal_v0_24__pxrReserved__::TfDelegatedCountDecrement(pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const*) /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/pathNode.h:746
    #7 0x564aa248fd20 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::_DecRef() const /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:177
    #8 0x564aa248fd20 in pxrInternal_v0_24__pxrReserved__::Sdf_PathNodeHandleImpl<pxrInternal_v0_24__pxrReserved__::Sdf_Pool<pxrInternal_v0_24__pxrReserved__::Sdf_PathPrimTag, 24u, 8u, 16384u>::Handle, true, pxrInternal_v0_24__pxrReserved__::Sdf_PathNode const>::~Sdf_PathNodeHandleImpl() /mnt/c/Users/HomePc/Fuzzing/linuxTarget/usd/OpenUSD/pxr/usd/sdf/path.h:97
AddressSanitizer:DEADLYSIGNAL
AddressSanitizer: nested bug in the same thread, aborting.
```


### PoC
1. Upload all proof-of-concept file [poc.usd.zip](https://github.com/user-attachments/files/17690595/poc.usd.zip)
3. Put any additional instructions or explanation for executing the proof-of-concept here
A crafted .usd file is attached, which triggers the vulnerability when loaded into any of the affected tools. This issue has been successfully reproduced in both Linux and macOS environments.

- Build the OpenUSD tools using the provided build instructions:
```
git clone https://github.com/PixarAnimationStudios/OpenUSD.git
python3 OpenUSD/build_scripts/build_usd.py ./install -j4 --no-python

cd ./install/bin
./sdfdump /path/to/poc.usd
```

- Run one of the vulnerable tools (e.g., `sdffilter`) with the provided crafted `.usd` file.
```
./sdffilter /path/to/crafted_file.usd
```


### Impact
OpenUSD, managed by the Alliance for OpenUSD (AOUSD), is widely adopted by major organizations such as Apple, NVIDIA, Autodesk, and Pixar. It serves as a key standard in industries like film, animation, gaming, AR/VR, and simulation. Exploitation of this vulnerability could lead to severe consequences, including system compromise, unauthorized data access, and disruption of services relying on OpenUSD. Given its critical role in 3D content creation and its widespread use, this vulnerability poses a significant threat to system security and data integrity. Immediate action is required to patch the issue and prevent potential security breaches.

### Credit 
- Song Hyun Bae ( @bshyuunn )

## References
- https://github.com/PixarAnimationStudios/OpenUSD/security/advisories/GHSA-58p5-r2f6-g2cj
- https://github.com/PixarAnimationStudios/OpenUSD/commit/0d74f31fe64310791e274e587c9926335e9db9db
- https://github.com/PixarAnimationStudios/OpenUSD
