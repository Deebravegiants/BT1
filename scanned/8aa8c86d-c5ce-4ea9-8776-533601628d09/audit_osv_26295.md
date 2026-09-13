# [M] mfd: qcom-spmi-pmic: Fix revid implementation

## Summary
Severity: Medium
Advisory: CVE-2023-52765
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-21
Source: https://osv.dev/vulnerability/CVE-2023-52765
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.64, >=6.2.0 <6.5.13, >=6.6.0 <6.6.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

mfd: qcom-spmi-pmic: Fix revid implementation

The Qualcomm SPMI PMIC revid implementation is broken in multiple ways.

First, it assumes that just because the sibling base device has been
registered that means that it is also bound to a driver, which may not
be the case (e.g. due to probe deferral or asynchronous probe). This
could trigger a NULL-pointer dereference when attempting to access the
driver data of the unbound device.

Second, it accesses driver data of a sibling device directly and without
any locking, which means that the driver data may be freed while it is
being accessed (e.g. on driver unbind).

Third, it leaks a struct device reference to the sibling device which is
looked up using the spmi_device_from_of() every time a function (child)
device is calling the revid function (e.g. on probe).

Fix this mess by reimplementing the revid lookup so that it is done only
at probe of the PMIC device; the base device fetches the revid info from
the hardware, while any secondary SPMI device fetches the information
from the base device and caches it so that it can be accessed safely
from its children. If the base device has not been probed yet then probe
of a secondary device is deferred.

## References
- https://git.kernel.org/stable/c/4ce77b023d42a9f1062eecf438df1af4b4072eb2
- https://git.kernel.org/stable/c/7b439aaa62fee474a0d84d67a25f4984467e7b95
- https://git.kernel.org/stable/c/affae18838db5e6b463ee30c821385695af56dc2
- https://git.kernel.org/stable/c/db98de0809f12b0edb9cd1be78e1ec1bfeba8f40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52765.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52765
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
