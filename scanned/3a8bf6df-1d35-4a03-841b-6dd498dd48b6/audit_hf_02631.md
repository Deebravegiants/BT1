# [M] Incorrect Template Removal on removeTemplate()

## Summary
Severity: Medium
Contest weight: 0.5900
Dataset id: 14248
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The removeTemplate() function of KPITokensManager contract removes a template from the templates array. The removed template is selected by the caller (owner) based on the template ID specified in the input parameter _id. To get the actual array index of the template, the function uses the templateIdToIndex mapping. There is an issue in the implementation of this function. Specifically, if the removed template is not the last item in the array, the function does not delete the respective templateIdToIndex. As a result, if the user calls removeTemplate() again with the same template ID, the function will delete the wrong template. Another related issue discovered during contract testing is that templateToIndex of the last template is assigned with an incorrect index on line [176], because the value of _index has been decremented by one on line [170-172] to facilitate templates index update on line [175]. As a result, the last template will be assigned with an incorrect index which compromises the correctness of templateToIndex.
Here is an example of what could go wrong. The user removes a template of id 0. The implementation correctly removes the template of id 0, but then assigns templateIdToIndex[10] to 0. As a result, the owner can not remove the template with id 10 because templateIdToIndex[10] returns 0 (on line [168]), which does not pass the check on line [169]. The same issue can be found in the removeTemplate() function of the OraclesManager contract.

## Recommendation
For KPITokensManager, the bug can be remedied by deleting the template from the templateIdToIndex mapping on all occasions and fixing the _index value when assigning templateIdToIndex. The following snippet shows an example of how to mitigate this issue on line [174-179]:
```solidity
if (_lastTemplate.id != _id) {
    templates[_index] = _lastTemplate;
    templateIdToIndex[_lastTemplate.id] = _index + 1;
    delete templateIdToIndex[_id];
}
```
Alternatively, the function removeTemplate() can be rewritten as follows:
Carrot KPI
```solidity
function removeTemplate(uint256 _id) external override onlyOwner {
    uint256 _index = templateIdToIndex[_id];
    if (_index == 0) revert NonExistentTemplate();
    Template storage _lastTemplate = templates[templates.length - 1];
    if (_lastTemplate.id != _id) {
        templates[_index-1] = _lastTemplate;
        templateIdToIndex[_lastTemplate.id] = _index;
        delete templateIdToIndex[_id];
    }
    templates.pop();
    emit RemoveTemplate(_id);
}
```
The testing team also recommends adding extensive tests to ensure the updates work as expected.
