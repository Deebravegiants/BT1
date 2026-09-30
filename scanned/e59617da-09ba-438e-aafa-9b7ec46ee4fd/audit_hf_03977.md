# [M] Wrong index in removeInstrument function

## Summary
Severity: Medium
Contest weight: 0.1236
Dataset id: 20343
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The removeInstrument function in SyndrExchange.sol accesses the whitelist as instrumentWhitelist[instrIdx]. This is incorrect and should instead use instrumentWhitelist[instrument].
The functions addInstrument and removeInstrument are responsible for adding and removing instruments to the whitelist. There is a coding error in the removal function. The mapping is stored in the variable instrumentWhitelist which maps an instrument to a bool. This can be seen in the addInstrument function https://github.
The value of instrument is used as the index to map the bool value. However, in the removal function, instrIdx is wrongly used, which holds the index of the instrument. This makes it impossible to remove instruments correctly and thus is classified as high severity.
Inability to manage whitelisted instruments correctly.

## Recommendation
Replace instrIdx with instrument in the removal function.
