# [C] C-06 | No Access Control

## Summary
Severity: Critical
Contest weight: 0.3021
Dataset id: 2407
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The vulnerability in the LimitOrderHook contract arises due to the lack of access control in the beforeSwap() and afterSwap() hook callback functions, which are critical to the proper execution of limit orders during swaps. Specifically, the beforeSwap() function stores the tick value before a swap, while the afterSwap() function processes limit orders based on the state change between the previous and new ticks. However, these functions do not have proper access control to restrict who can invoke them. Without mechanisms like the onlyByPoolManager() modifier, unauthorized users can call these functions directly, including malicious actors who may manipulate swap behavior. This could lead to serious consequences such as unauthorized order executions, where users could trigger limit orders to be processed without them actually being filled or meet the conditions of the swap. For example, the executeOrder() function, which is designed to be executed only by the LimitOrderHook contract after a legitimate swap, can currently be called by any user. This allows for orders to be executed or cleared arbitrarily, completely undermining the protocol's limit order mechanism and breaking its core functionality. Given that these hooks are integral to the protocol's operation, this access control vulnerability has the potential to severely disrupt the system, leading to manipulation of the limit order functionality.

## Recommendation
Add onlyByPoolManager() of SafeCallback.sol in all hooks for access control.
