# [H] uniapi version 1.0.7 contained an information harvesting script.

## Summary
Severity: High
Advisory: GHSA-gvvw-rr8m-fj76
Ecosystem: PyPI
Published: 2025-01-27
Source: https://github.com/advisories/GHSA-gvvw-rr8m-fj76
Type: github-advisory

## Affected
- PyPI: `uniapi` — affected 1.0.7

## Details
uniapi version 1.0.7 introduces code that would execute on import of the module and download a script from a remote URL, and would then execute the downloaded script in a thread. The downloaded script would harvest system information and `POST` the information to another remote URL. This code was found in the PyPI release artifacts and was not present in the public GitHub repository.

## References
- https://github.com/kam193/package-campaigns/blob/main/pypi/campaigns/highly_suspicious/2025-01-uniapi.json
- https://github.com/pypa/advisory-database/tree/main/vulns/uniapi/PYSEC-2025-2.yaml
- https://inspector.pypi.io/project/uniapi/1.0.7/packages/0f/40/c6e06c22bbc22ef45f40bf5a7711763fa08fec4d16b4718d86fd60970131/uniapi-1.0.7.tar.gz/uniapi-1.0.7/uniapi/__init__.py#line.11
