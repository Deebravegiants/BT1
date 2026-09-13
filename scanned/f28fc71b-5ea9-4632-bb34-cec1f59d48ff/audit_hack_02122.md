# [H] Inconsistent usage of applyInterest

## Summary
Severity: High
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
# Email address

pauliax6@gmail.com


# Handle

paulius.eth


# Eth address

0x523B5b2Cc58A818667C22c862930B141f85d49DD


# Vulnerability details

It is unclear if the function applyInterest is supposed to return a new balance with the interest applied or only the accrued interest? There are various usages of it, some calls add the return value to the old amount:
return
    bond.amount +
    applyInterest(bond.amount, cumulativeYield, yieldQuotientFP);
and some not:

   balanceWithInterest = applyInterest(
            balance,
            yA.accumulatorFP,
            yieldQuotientFP
        );


# Impact

This makes the code misbehave and return the wrong values for the balance and accrued interest.


# Recommended mitigation steps

Make it consistent in all cases when calling this function.
