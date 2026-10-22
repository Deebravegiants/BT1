# [M] The Vault._update_debt() function should be

## Summary
Severity: Medium
Contest weight: 0.2615
Dataset id: 20176
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The Vault._update_debt() should be executed before the interests rate are modified by the Vault.set_variable_interest_parameters() function. The Vault._update_debt() function helps to accrue interest since the last update. The execution path: 1. It calls the function Vault._debt_interest_since_last_update(_debt_token) in order to calculate the token debt interest. 2. The Vault._debt_interest_since_last_update() function uses the Vault._current_interest_per_second() function in order to get the interest per second. 3. The Vault._current_interest_per_second() calls Vault._interest_rate_by_utilization() in order to get the interest rate. 4. The Vault._interest_rate_by_utilization() function calls the Vault._dynamic_interest_rate_low_utilization() or Vault._dynamic_interest_rate_high_utilization depending on the switch utilization. 5. The Vault._dynamic_interest_rate_low_utilization() is executed and it calls the Vault._min_interest_rate(). 6. Then, the Vault._min_interest_rate() function gets the value from the [self.interest_configuration_address][0]. So in the step 6, it gets the interest from the interest_configuration, then the interests are used in order to calculate the token debt. The Vault._update_debt() accrue interest since the last update, the function should be executed before the admin change the interest configuration via Vault.set_variable_interest_parameters() function. The reason is that the time that has already passed must be taken with the previous interest before the admin changes to the new interests rate. The protocol should accrue interest since the last update before change the interest rate configuration. If the admin change the interest rate, the new interest rate should be applied to the future time not to the time that has already passed. The time that has already passed should use the previous interest. It is unfair for the users because users expects interests changes to be applied after they were changed not to the past time the _update_debt has not been executed. • The Vault._update_debt() function. • The Vault._debt_interest_since_last_update function. • The Vault._current_interest_per_second() function. • The Vault._interest_rate_by_utilization() function. • The Vault._dynamic_interest_rate_low_utilization() function. • The Vault._dynamic_interest_rate_high_utilization() function. • The Vault._interest_configuration() function. • The Vault.set_variable_interest_parameters() function.

## Recommendation
Execute self._update_debt(address) before the interests are modified:
def set_variable_interest_parameters(
    _address: address,
    _min_interest_rate: uint256,
    _mid_interest_rate: uint256,
    _max_interest_rate: uint256,
    _rate_switch_utilization: uint256,
):
    assert msg.sender == self.admin, "unauthorized"
    self._update_debt(_address)
    self.interest_configuration[_address] = [
        _min_interest_rate,
        _mid_interest_rate,
        _max_interest_rate,
        _rate_switch_utilization,
    ]
