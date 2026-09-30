# [M] Proper initializerRunAlways() Modiﬁer

## Summary
Severity: Medium
Contest weight: 0.4201
Dataset id: 11683
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Augmented protocol makes certain extensions on the initialization logic, including the new initializerRunAlways modifier. Note that unlike constructors, the initializer functions must be manually invoked. And this applies both to deploying an Initializable contract, as well as extending an Initializable contract via inheritance. It should be emphasized that when used with inheritance, parent initializers with initializerRunAlways modifier are not protected from multiple calls by another initializer. To elaborate, we show below the related initializerRunAlways modiﬁer. It comes to our attention that it contains the inclusion of body functions twice (lines 54 and 59). The two-time invocation may bring unexpected execution results from the included function body.
```solidity
modifier initializerRunAlways(uint256 localRevision) {
    uint256 topRevision = getRevision();
    (bool initializing, bool skip) = _preInitializer(localRevision, topRevision);
    if (!skip) {
        lastInitializingRevision = localRevision;
    }
    if (!skip) {
        lastInitializedRevision = localRevision;
    }
    if (!initializing) {
        lastInitializedRevision = topRevision;
    }
    lastInitializingRevision = 0;
}
```

## Recommendation
Revise the initializerRunAlways modifier to include the function body only once.
