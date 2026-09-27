# [M] Build corruption when using `PYO3_CONFIG_FILE` environment variable

## Summary
Severity: Medium
Advisory: GHSA-vxcf-c7mx-pg53
Ecosystem: crates.io
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-vxcf-c7mx-pg53
Type: github-advisory

## Affected
- crates.io: `pyo3` — affected >=0.23.0 <0.23.3

## Details
In PyO3 0.23.0 the `PYO3_CONFIG_FILE` environment variable used to configure builds regressed such that changing the environment variable would no longer trigger PyO3 to reconfigure and recompile. In combination with workflows using tools such as `maturin` to build for multiple versions in a single build, this leads to Python wheels being compiled against the wrong Python API version.

All users who distribute artefacts for multiple Python versions are encouraged to update and rebuild with PyO3 0.23.3. Affected wheels produced from PyO3 0.23.0 through 0.23.2 are highly unstable and will crash the Python interpreter in unpredictable ways.

## References
- https://github.com/PyO3/pyo3/issues/4757
- https://github.com/PyO3/pyo3
- https://rustsec.org/advisories/RUSTSEC-2024-0409.html
