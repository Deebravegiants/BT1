# [M] Collateral parameters can be overwritten

## Summary
Severity: Medium
Contest weight: 0.2472
Dataset id: 1391
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability lies in the collateral whitelist management function that allows the contract owner to repeatedly add the same collateral token as the first entry in the validCollateral list. The function attempts to prevent duplicate entries by checking that validCollateral[0] != _collateral before performing a require that the collateral has not been registered yet. However, when the caller supplies the address that is already stored at index 0, the inequality comparison evaluates to false, causing the whole conditional block—including the require that would reject an existing token—to be skipped. Consequently, the function pushes the duplicate address onto the validCollateral array and overwrites the CollateralParams mapping entry for that token with the newly supplied parameters. This logical flaw constitutes an insufficient uniqueness validation bug in a whitelist management routine, which permits overwriting of critical protocol configuration such as the minimum collateralisation ratio, oracle address, decimal precision, and price‑curve contract for the first listed collateral. The impact is that a malicious or compromised owner can modify these parameters at will, potentially lowering the required safety margin, redirecting price feeds to manipulated oracles, or otherwise breaking the accounting assumptions that keep loans properly collateralised. When the altered parameters are used by downstream borrowing and liquidation logic, borrowers may experience unexpected liquidations, their collateral value may appear to disappear from the UI, or loans may be approved under insecure conditions, leading to loss of funds for users and undermining confidence in the protocol. The issue manifests only when the addCollateral function is called with a collateral address that already occupies the first slot of the validCollateral array; calls with any other address are correctly guarded. It was discovered during a Code4rena audit that examined the whitelist implementation and identified that the existence check was inadvertently bypassed for the first element. The bug can be subtle because the require statement is present and appears to enforce uniqueness, yet the surrounding logical condition renders it ineffective for the specific case of the first entry, allowing duplicate entries to go unnoticed in the array while silently overwriting parameters. To remediate the problem, the contract should enforce a proper uniqueness check that does not rely on a single positional comparison. A robust solution is to verify that the collateral address is not already present in the whitelist regardless of its position, for example by checking that collateralParams[_collateral].index is zero (indicating an unregistered token) or by maintaining a dedicated mapping of registered tokens and rejecting any attempt to add an already‑registered address. This ensures that collateral parameters cannot be overwritten and that the whitelist remains invariant, preserving the intended economic guarantees of the protocol.

## Proof of Concept
Owner calls `addCollateral(collateral=validCollateral[0])`:
    
    function addCollateral(
        address _collateral,
        uint256 _minRatio,
        address _oracle,
        uint256 _decimals,
        address _priceCurve, 
        bool _isWrapped
    ) external onlyOwner {
        checkContract(_collateral);
        checkContract(_oracle);
        checkContract(_priceCurve);
        // If collateral list is not 0, and if the 0th index is not equal to this collateral,
        // then if index is 0 that means it is not set yet.
        // @audit evaluates validCollateral[0] != validCollateral[0] which is obv. false => skips require check
        if (validCollateral.length != 0 && validCollateral[0] != _collateral) {
            require(collateralParams[_collateral].index == 0, "collateral already exists");
        }
    
        validCollateral.push(_collateral);
        // overwrites parameters
        collateralParams[_collateral] = CollateralParams(
            _minRatio,
            _oracle,
            _decimals,
            true,
            _priceCurve,
            validCollateral.length - 1, 
            _isWrapped
        );
    }

## Recommendation
Fix the check. It should be something like:
    
    if (validCollateral.length > 0) {
        require(collateralParams[_collateral].index == 0 && validCollateral[0] != _collateral, "collateral already exists");
    }
