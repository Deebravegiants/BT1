# [M] Vulnerability in Outdated Web Plug-in resolve-url-loader

## Summary
Severity: Medium
Contest weight: 0.0857
Dataset id: 12196
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
It is known that during the web development, it is necessary to import a number of third-party or unoffcial libraries. Therefore, validating the security of dependent libraries is critical and necessary. During our analysis, we found that the imported library resolve-url-loader v3.1.1 contains several known vulnerabilities, the most severe one could lead to denial-of-service to block normal services. More details can be found at https://npmjs.com/advisories/1556.

## Recommendation
Upgrade the dependent resolve-url-loader v3.1.1 to version v3.1.2 or above. Moreover, we highly recommend executing npm audit fix to check the existence of any 0day vulnerabilities after the change of dependent libraries.
