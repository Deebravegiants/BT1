# [H] CVE-2020-11886

## Summary
Severity: High
Advisory: CVE-2020-11886
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-04-17
Source: https://osv.dev/vulnerability/CVE-2020-11886
Type: osv

## Details
OpenNMS Horizon and Meridian allows HQL Injection in element/nodeList.htm (aka the NodeListController) via snmpParm or snmpParmValue to addCriteriaForSnmpParm. This affects Horizon before 25.2.1, Meridian 2019 before 2019.1.4, Meridian 2018 before 2018.1.16, and Meridian 2017 before 2017.1.21.

## References
- https://issues.opennms.org/browse/NMS-12572
