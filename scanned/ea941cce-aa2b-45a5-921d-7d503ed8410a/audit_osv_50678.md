# [M] CVE-2020-27820

## Summary
Severity: Medium
Advisory: CVE-2020-27820
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-11-03
Source: https://osv.dev/vulnerability/CVE-2020-27820
Type: osv

## Details
A vulnerability was found in Linux kernel, where a use-after-frees in nouveau's postclose() handler could happen if removing device (that is not common to remove video card physically without power-off, but same happens if "unbind" the driver).

## References
- https://lore.kernel.org/dri-devel/20201103194912.184413-2-jcline%40redhat.com/
- https://lore.kernel.org/dri-devel/20201103194912.184413-3-jcline%40redhat.com/
- https://lore.kernel.org/dri-devel/20201103194912.184413-4-jcline%40redhat.com/
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1901726
