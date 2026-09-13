# [H] skia-python vendors vulnerable libfreetype because of pinned cibuildwheel version

## Summary
Severity: High
Advisory: GHSA-2mhw-8qcg-gr96
CWE: CWE-1395, CWE-787
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-2mhw-8qcg-gr96
Type: github-advisory

## Affected
- PyPI: `skia-python` — affected 144.0
- PyPI: `skia-python` — affected >=0 <144.0.post1

## Details
### Impact

The Linux wheels for skia-python vendor a vulnerable version of
libfreetype that is affected by CVE-2025-27363 [1].

The root cause is a chain of unfortunate events:

1. skia-python builds wheels using pinned pypa/cibuildwheel@2.21.3 [2]

2. cibuildwheel 2.21.3 in turn pins manylinux container images [3]

3. In these images, version 2.9.1-9.el8 of RedHat package freetype is
*preinstalled*. This package version is vulnerable and has since been
patched in 2.9.1-10.

4. During the skia-python Linux build, libfreetype is vendored from the
system, resulting in skia-python.libs/libfreetype-29a7443c.so.6.16.1

[ To find the provenance of your vendored libfreetype, we extracted the
8-character hash of the original binary file that is added during the
build process (29a7443c), and matched it against our database of hashes
all historic Red Hat, Debian and Ubuntu releases of freetype. ]

5. Because freetype is only a *transitive* dependency of the packages
explicitly installed by the build script [4], it is not upgraded to the
patched version [4].

5. As a result, the published wheels embed a vulnerable libfreetype,
even though patched packages are available upstream.

This appears to be a broader manylinux ecosystem issue. The base images
do not enforce that `yum update` runs on container start, so
preinstalled libraries may remain vulnerable indefinitely.


### Patches

> In the case of skia-python, the solution is to explicitly install freetype in the build process and rebuild the wheels.

The original report was suggesting the above, but in the current `build_Linux.sh` script, the patched `freetype-devel` version 2.9.1-10 gets installed as a dependency. It's just that we need to rebuild the wheel for a new release.

### Workarounds

Users must upgrade the wheel package after release.

### References

1. https://nvd.nist.gov/vuln/detail/CVE-2025-27363
2. https://github.com/kyamagu/skia-python/blob/9ffb045811f9b5508e152302d5b81aadca6edd8d/.github/workflows/ci.yml#L38
3. https://github.com/pypa/cibuildwheel/blob/v2.21.3/cibuildwheel/resources/pinned_docker_images.cfg
4. https://github.com/kyamagu/skia-python/blob/9ffb045811f9b5508e152302d5b81aadca6edd8d/scripts/build_Linux.sh#L6

## References
- https://github.com/kyamagu/skia-python/security/advisories/GHSA-2mhw-8qcg-gr96
- https://nvd.nist.gov/vuln/detail/CVE-2025-27363
- https://github.com/kyamagu/skia-python
