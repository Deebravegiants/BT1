# [C] Python Command Injection in imartinez/privategpt

## Summary
Severity: Critical
Advisory: CVE-2024-4343
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-14
Source: https://osv.dev/vulnerability/CVE-2024-4343
Type: osv

## Details
A Python command injection vulnerability exists in the `SagemakerLLM` class's `complete()` method within `./private_gpt/components/llm/custom/sagemaker.py` of the imartinez/privategpt application, versions up to and including 0.3.0. The vulnerability arises due to the use of the `eval()` function to parse a string received from a remote AWS SageMaker LLM endpoint into a dictionary. This method of parsing is unsafe as it can execute arbitrary Python code contained within the response. An attacker can exploit this vulnerability by manipulating the response from the AWS SageMaker LLM endpoint to include malicious Python code, leading to potential execution of arbitrary commands on the system hosting the application. The issue is fixed in version 0.6.0.

## References
- https://huntr.com/bounties/1d1e8f06-ec45-4b17-ae24-b83a41304c15
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4343.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4343
- https://github.com/imartinez/privategpt/commit/86368c61760c9cee5d977131d23ad2a3e063cbe9
