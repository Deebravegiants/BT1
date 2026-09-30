# [H] Decimals not Handled by the Application Frontend

## Summary
Severity: High
Contest weight: 0.2995
Dataset id: 2895
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
In allyourbase.virtual.tech a user can manually enter 1.(decimal) numbers in the deposit amount. Consequently the frontend will display an exponential amount (see image) and the session balance will be displayed using this convention.
In the image: A user introduced a decimal value 1.0…0001(14 decimals) in the session balance. When submitting the app processes that amount as an exponential. If the user guesses an incorrect prediction the “Session balance” is still displaying the exponential value without any change.
Since the application relies on blockchain technology, these rounding errors could lead to issues in the calculations or even just gas griefing, as the backend might not be able to handle decimal values properly.
In the image: After finishing the session, the virtual balance is updated with exponentials.

In the image: Another example with 17 decimals.
In the image: The frontend is displaying at least 1 in session balance and the bet is for exactly $1. Hence, when hitting submit the app displays insufficient balance. The introduction of decimals are not handled by the app.

This particular finding is classified as high since it is related to gaming finance (at least from the frontend perspective), and the app is displaying amounts in decimals (something that might not be expected by the backend).

## Recommendation
Revise the permitted input for the deposit amount. Although users are expected to enter whole numbers, the application currently accepts decimals. This could lead to rounding errors, as the application does not notify users that decimals might not be supported.
