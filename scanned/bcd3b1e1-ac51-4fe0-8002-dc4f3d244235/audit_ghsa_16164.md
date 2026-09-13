# [H] LLama Factory Remote OS Command Injection Vulnerability

## Summary
Severity: High
Advisory: GHSA-hj3w-wrh4-44vp
CVE: CVE-2024-52803
CWE: CWE-78, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-11-21
Source: https://github.com/advisories/GHSA-hj3w-wrh4-44vp
Type: github-advisory

## Affected
- PyPI: `llamafactory` — affected >=0 <0.9.1

## Details
## Summary

A critical remote OS command injection vulnerability has been identified in the Llama Factory training process. This vulnerability arises from improper handling of user input, allowing malicious actors to execute arbitrary OS commands on the host system. The issue is caused by insecure usage of the `Popen` function with `shell=True`, coupled with unsanitized user input. Immediate remediation is required to mitigate the risk.

## Affected Version

Llama Factory versions **<=0.9.0** are affected by this vulnerability.

## Impact

Exploitation of this vulnerability allows attackers to:

1. Execute arbitrary OS commands on the server.
2. Potentially compromise sensitive data or escalate privileges.
3. Deploy malware or create persistent backdoors in the system.

This significantly increases the risk of data breaches and operational disruption.

## Root Cause

The vulnerability originates from the training process where the `output_dir` value, obtained from the user input, is injected into the popen function without any sanitization. Furthermore, popen is invoked in a unsafe way by enabling the interact shell (`shell=True`), leading to remote OS command injection vulnerability.

Vulnerable snippet: 

```python
# https://github.com/hiyouga/LLaMA-Factory/blob/bd639a137e6f46e1a0005cc91572f5f1ec894f74/src/llamafactory/webui/runner.py#L304-L323
def _launch(self, data: Dict["Component", Any], do_train: bool) -> Generator[Dict["Component", Any], None, None]:
				...
        args = self._parse_train_args(data) if do_train else self._parse_eval_args(data)
				...
        self.trainer = Popen(f"llamafactory-cli train {save_cmd(args)}", env=env, shell=True)
        yield from self.monitor()
```

## Proof of Concept (PoC)

### Steps to Reproduce

- Deploy llama factory

- Execute the exploitation script from: https://gist.github.com/superboy-zjc/f2d2b93ae511c445ba97e144b70e534d

  ```bash
  python3 llama-factory-rce.py --url http://127.0.0.1:7861 --cmd "curl XXX" --trace
  ```

![llama-factory-rce](https://api.2h0ng.wiki:443/noteimages/2024/11/21/00-33-37-5347128a141f8765e7d218c89d94162a.gif)

Bad actors are able to execute any OS command as they want.

## Remediation Recommendations

**Avoid using `shell=True` in `Popen`.**

- Instead, pass the command and its arguments as a list. This prevents user inputs from being executed as part of a shell command.

```python
cmd = [
    "llamafactory-cli",
    "train", 
  	*save_cmd(args).split(),
]
self.trainer = Popen(cmd, env=env)
```

## References
- https://github.com/hiyouga/LLaMA-Factory/security/advisories/GHSA-hj3w-wrh4-44vp
- https://nvd.nist.gov/vuln/detail/CVE-2024-52803
- https://github.com/hiyouga/LLaMA-Factory/commit/b3aa80d54a67da45e9e237e349486fb9c162b2ac
- https://gist.github.com/superboy-zjc/f2d2b93ae511c445ba97e144b70e534d
- https://github.com/hiyouga/LLaMA-Factory
