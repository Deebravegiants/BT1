# [C] CVE-2020-15243

## Summary
Severity: Critical
Advisory: CVE-2020-15243
Aliases: GHSA-8g9m-jx26-qp4h
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-10-08
Source: https://osv.dev/vulnerability/CVE-2020-15243
Type: osv

## Details
Affected versions of Smartstore have a missing WebApi Authentication attribute. This vulnerability affects Smartstore shops in version 4.0.0 & 4.0.1 which have installed and activated the Web API plugin. Users of Smartstore 4.0.0 and 4.0.1 must merge their repository with 4.0.x or overwrite the file SmartStore.Web.Framework in the */bin* directory of the deployed shop with this file. As a workaround without updating uninstall the Web API plugin to close this vulnerability.

## References
- https://github.com/smartstore/SmartStoreNET/security/advisories/GHSA-8g9m-jx26-qp4h
