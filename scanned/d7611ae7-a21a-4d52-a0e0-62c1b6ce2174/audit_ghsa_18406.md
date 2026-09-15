# [M] MS SWIFT Deserialization RCE Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-r54c-2xmf-2cf3
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-31
Source: https://github.com/advisories/GHSA-r54c-2xmf-2cf3
Type: github-advisory

## Affected
- PyPI: `ms-swift` — affected >=0

## Details
This appears to be a security vulnerability report describing a remote code execution (RCE) exploit in the ms-swift framework through malicious pickle deserialization in adapter model files. The vulnerability allows arbitrary command execution when loading specially crafted adapter models from ModelScope.

This occurs when using machine torch version < 2.6.0, while ms-swift accepts torch version >= 2.0

**I. Detailed Description:**
1. Install ms-swift
```
pip install ms-swift -U
```

2. Start web-ui
```
swift web-ui --lang en
```

3. After startup, you can access [http://localhost:7860/](http://localhost:7860/) through your browser to see the launched fine-tuning framework program

4. Upload an adapter model repository (cyjhhh/lora_adapter_4_llama3) on ModelScope, where the lora/adapter_model.bin file is generated through the following code:
```python
import torch, pickle, os

class MaliciousPayload:
   def __reduce__(self):
       return (os.system, ("touch /tmp/malicious.txt",))  # Arbitrary command

malicious_data = {
   "v_head.summary.weight": MaliciousPayload(),
   "v_head.summary.bias": torch.randn(10)
}

if __name__ == "__main__":
   with open("adapter_model.bin", "wb") as f:
       pickle.dump(malicious_data, f)
```

5. First training submission: First, fill in the required parameters in the LLM Training interface, including Model id and Dataset Code, and configure the following in the Other params section of Advanced settings

6. Click Begin to submit. You can see the backend command running as follows

7. By reading the ms-swift source code, swift.llm.model.utils#safe_snapshot_download() and modelscope.hub.utils.utils#get_cache_dir(), we can see that adapters are downloaded locally to the path ~/.cache/modelscope. Therefore, the complete local path for the specified remote adapters after download is:
```
~/.cache/modelscope/hub/models/cyjhhh/lora_adapter_4_llama3
```
Wait for the first submission program until the adapters download is complete, then you can click "kill running task" on the page to terminate the first training

8. Second training submission, configure the page parameters as follows

Click submit to see the backend command running as follows

9. After waiting for a while, you can see that torch.load() loaded the malicious adapter_model.bin file and successfully executed the command. Related execution information can also be seen in the log file corresponding to --logging_dir

10. Note (Prerequisites)
Requires machine torch version < 2.6.0, while ms-swift accepts torch version >= 2.0

**II. Vulnerability Proof:**
1. Remote downloaded adapter malicious model: [[lora_adapter_4_llama3](https://www.modelscope.cn/models/cyjhhh/lora_adapter_4_llama3/files)](https://www.modelscope.cn/models/cyjhhh/lora_adapter_4_llama3/files)
2. For the second training submission, it's recommended to follow the parameters shown in the screenshots above for reproduction, as it will validate the target modules specified in the base model and adapter config. If they don't match, the program will terminate early. It's also recommended to select the same dataset content as shown in the screenshots
3. This report only reproduces RCE for one entry point (single path). In reality, there are more than one path in the code that can cause deserialization RCE

**III. Fix Solution:**
```
SWIFT has disabled torch.load operations from 3.7 or later.
```

## Author

* Discovered by: [TencentAISec](https://github.com/TencentAISec)
* Contact: *[security@tencent.com](mailto:security@tencent.com)*

## References
- https://github.com/modelscope/ms-swift/security/advisories/GHSA-r54c-2xmf-2cf3
- https://github.com/modelscope/ms-swift/commit/cc47463bcd25a8720437cf945130f43052eec5e4
- https://github.com/modelscope/ms-swift
