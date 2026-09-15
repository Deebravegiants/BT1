# [M] M-08 Unmitigated

## Summary
Severity: Medium
Source: https://github.com/code-423n4/2023-08-goodentry/blob/71c0c0eca8af957202ccdbf5ce2f2a514ffe2e24/contracts/helper/V3Proxy.sol#L156
Type: audit-issue

## Details
# Lines of code

https://github.com/code-423n4/2023-08-goodentry/blob/71c0c0eca8af957202ccdbf5ce2f2a514ffe2e24/contracts/helper/V3Proxy.sol#L156
https://github.com/code-423n4/2023-08-goodentry/blob/71c0c0eca8af957202ccdbf5ce2f2a514ffe2e24/contracts/helper/V3Proxy.sol#L174
https://github.com/code-423n4/2023-08-goodentry/blob/71c0c0eca8af957202ccdbf5ce2f2a514ffe2e24/contracts/helper/V3Proxy.sol#L192


# Vulnerability details

## Comments

The success of low-level calls is not checked in V3Proxy. 
If msg.sender is a contract and the fallback function has additional logic, the protocol will succeed transfer by default, which will result in the loss of user funds.

## Mitigation

There is no corresponding repair link posted in the readme, and there are no related repairs in https://github.com/GoodEntry-io/ge.
The fix link in the issue is marked as https://github.com/GoodEntry-io/ge/pull/3/files. I think this is a misunderstanding. The sponsor mistook the issue for transfer and modified it to a call.

## Suggestion

What needs to be fixed is the low-level calls in the V3Proxy contract. Their success return values ​​should be checked for success.
Code positioning can be done based on the three links I mentioned above.

## Conclusion

Need repair


## Assessed type

call/delegatecall
