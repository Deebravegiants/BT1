# [M] Quadratic resource consumption in validating existence of initiating messages

## Summary
Severity: Medium
Contest weight: 0.1333
Dataset id: 5742
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Contains iterates through each log in the entire block, requiring all receipts from the block being processed, that is a O(n) complexity with n being the block size. As this function is called for each executing message to check if the corresponding initiating message exists, in the worst case scenario this is O(n^2) with the size of the block. With the cost of producing logs and executing messages being low in terms of gas, this is likely to result in significant resource consumption above the necessary.  
Since the consolidation process is already O(m^2) with the number of chains, this could lead to the impossibility of proving a state transition as the number of chains scale. If other issues are found that further compound resource consumption, this could lead to more severe impact even with small number of chains in the dependency set.

## Recommendation
This should be corrected to consume sublinear resources. For example a simple proof of existence would be O(log(n)). Other approaches such as indexing all logs by message hash could be explored.
