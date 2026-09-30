# [M] MS SWIFT WEB-UI RCE Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7c78-rm87-5673
CVE: CVE-2025-41419
CWE: CWE-117
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-7c78-rm87-5673
Type: github-advisory

## Affected
- PyPI: `ms-swift` — affected >=0 <3.7.0

## Details
**I. Detailed Description:** 

This includes scenarios, screenshots, vulnerability reproduction methods. For account-related vulnerabilities, please provide test accounts. If the reproduction process is complex, you may record a video, upload it to Taopan, and attach the link.

1. Install ms-swift
   ```
   pip install ms-swift -U
   ```

2. Start web-ui
   ```
   swift web-ui --lang en
   ```

3. After startup, access through browser at [http://localhost:7860/](http://localhost:7860/) to see the launched fine-tuning framework program

4. Fill in necessary parameters
   In the LLM Training interface, fill in required parameters including Model id, Dataset Code. The --output_dir can be filled arbitrarily as it will be modified later through packet capture

5. Click Begin to start training. Capture packets and modify the parameter corresponding to --output_dir

   You can see the concatenated command being executed in the terminal where web-ui was started

6. Wait for the program to run (testing shows it requires at least 5 minutes), and you can observe the effect of command execution creating files

**II. Vulnerability Proof (Write POC here):**
```
/tmp/xxx'; touch /tmp/inject_success_1; #
```

**III. Fix Solution:**
1. The swift.ui.llm_train.llm_train.LLMTrain#train() method should not directly concatenate parameters with commands after receiving commands from the frontend
2. The swift.ui.llm_train.llm_train.LLMTrain#train_local() method should not use os.system for execution, but should be changed to subprocess.run([cmd, arg1, arg2...]) format

## Author

* Discovered by: [TencentAISec](https://github.com/TencentAISec)
* Contact: *[security@tencent.com](mailto:security@tencent.com)*

## References
- https://github.com/modelscope/ms-swift/security/advisories/GHSA-7c78-rm87-5673
- https://github.com/modelscope/ms-swift/commit/32f09e9b0a44f19d44210e2b5b47c58ab01740e1
- https://github.com/modelscope/ms-swift
