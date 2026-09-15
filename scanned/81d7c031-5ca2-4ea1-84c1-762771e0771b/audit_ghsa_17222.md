# [M] Grav is vulnerable to a DOS on the admin panel

## Summary
Severity: Medium
Advisory: GHSA-x62q-p736-3997
CVE: CVE-2025-66303
CWE: CWE-400
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-x62q-p736-3997
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
# DOS on the admin panel
**Severity Rating:** Medium 

**Vector:** Denial Of Service

**CVE:** XXX

**CWE:** 400 - Uncontrolled Resource Consumption

**CVSS Score:** 4.9

**CVSS Vector:** CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H

## Analysis

A Denial of Service (DoS) vulnerability has been identified in the application related to the handling of `scheduled_at` parameters. Specifically, the application fails to properly sanitize input for cron expressions. By manipulating the `scheduled_at` parameter with a malicious input, such as a single quote, the application admin panel becomes non-functional, causing significant disruptions to administrative operations.

The only way to recover from this issue is to manually access the host server and modify the `backup.yaml` file to correct the corrupted cron expression

## Proof of Concept

1) Change the value of `scheduled_at` parameter to `'` as shown in the following figures at the `http://127.0.0.1/admin/tools` endpoint, and observe the response in the second figure:
  ![gravdos2](https://github.com/user-attachments/assets/b2d8935f-c8ba-4eda-998a-8a20b3d5ef7c)
  *Figure: Http request on tool endpoint*
![gravdos3](https://github.com/user-attachments/assets/2a283254-316a-45b3-a5ac-6804e2494cd7)
  *Figure: Http response on tool endpoint*

2) When trying to access the admin panel, the panel is broken as shown in the following figure. Additionally, the value change is reflected in the `backup.yaml` file, as shown in the second figure:
  ![gravdos4](https://github.com/user-attachments/assets/1257adcb-96c4-4b30-864e-9aa01e410ded)
  *Figure: Error message view*
![gravdos5](https://github.com/user-attachments/assets/4cef7c49-6a1e-4414-8332-3195aa2dfc77)
  *Figure: Backup.yaml file*


## Workarounds
No workaround is currently known

# Timeline
**2024-07-24** Issue identified

**2024-09-27** Vendor contacted


# About X41 D-Sec GmbH
X41 is an expert provider for application security services.
Having extensive industry experience and expertise in the area of information
security, a strong core security team of world class security experts enables
X41 to perform premium security services.

Fields of expertise in the area of application security are security centered
code reviews, binary reverse engineering and vulnerability discovery.
Custom research and IT security consulting and support services are core
competencies of X41.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-x62q-p736-3997
- https://nvd.nist.gov/vuln/detail/CVE-2025-66303
- https://github.com/getgrav/grav/commit/9d11094e4133f059688fad1e00dbe96fb6e3ead7
- https://github.com/getgrav/grav
