# [M] Use of "infinity" as an input to datetime and date fields causes infinite loop in pydantic

## Summary
Severity: Medium
Advisory: GHSA-5jqp-qgf6-3pvh
CVE: CVE-2021-29510
CWE: CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-13
Source: https://github.com/advisories/GHSA-5jqp-qgf6-3pvh
Type: github-advisory

## Affected
- PyPI: `pydantic` — affected >=0 <1.6.2
- PyPI: `pydantic` — affected >=1.8 <1.8.2
- PyPI: `pydantic` — affected >=1.7 <1.7.4

## Details
Impact

Passing either 'infinity', 'inf' or float('inf') (or their negatives) to datetime or date fields causes validation to run forever with 100% CPU usage (on one CPU).
Patches

Pydantic is be patched with fixes available in the following versions:

    v1.8.2
    v1.7.4
    v1.6.2

All these versions are available on pypi, and will be available on conda-forge soon.

See the changelog for details.
Workarounds

If you absolutely can't upgrade, you can work around this risk using a validator to catch these values, brief demo:

from datetime import date
from pydantic import BaseModel, validator

class DemoModel(BaseModel):
    date_of_birth: date

    @validator('date_of_birth', pre=True)
    def skip_infinite_values(cls, v):
        try:
            seconds = float(v)
        except (ValueError, TypeError):
            return v
        else:
            if seconds == float('inf'):
                return date.max
            elif seconds == float('-inf'):
                return date.min
            else:
                return seconds

Note: this is not an ideal solution (in particular you'll need a slightly different function for datetimes), instead of a hack like this you should upgrade pydantic.

If you are not using v1.8.x, v1.7.x or v1.6.x and are unable to upgrade to a fixed version of pydantic, please create an issue requesting a back-port, and we will endeavour to release a patch for earlier versions of pydantic.
References

This was fixed in commit 7e83fdd.

## References
- https://github.com/samuelcolvin/pydantic/security/advisories/GHSA-5jqp-qgf6-3pvh
- https://nvd.nist.gov/vuln/detail/CVE-2021-29510
- https://github.com/pydantic/pydantic/commit/1c24f1d74ba95ea985b50bdc001ce96c813229aa
- https://github.com/pydantic/pydantic/commit/80e0dd3f752bef145dce12f160d262bb40ec8d47
- https://github.com/pydantic/pydantic/commit/bdde15b7b947c94ca00fd6eb92da8db390a13520
- https://github.com/samuelcolvin/pydantic/commit/7e83fdd2563ffac081db7ecdf1affa65ef38c468
- https://github.com/pydantic/pydantic
- https://github.com/pypa/advisory-database/tree/main/vulns/pydantic/PYSEC-2021-47.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/S2HT266L6Q7H6ICP7DFGXOGBJHNNKMKB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UEFWM7DYKD2ZHE7R5YT5EQWJPV4ZKYRB
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UMKAJX4O6IGBBCE32CO2G7PZQCCQSBLV
