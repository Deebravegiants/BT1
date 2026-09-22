# [?] Fix quit race condition for cmd package tests (#372)

## Summary
Severity: Unknown
Chain: Starknet
Component: NethermindEth/juno
Published: 2022-08-26
Source: https://github.com/NethermindEth/juno/commit/2354ee8ed8dce23b8276d9509444df3b9bdec56c
Type: security-commit

## Details
Fix quit race condition for cmd package tests (#372)

The tests in cmd package need to send a quit signal through an exit channel
which simulates the user's behaviour to interrupt the juno. However, the test
also predicates that Run() of StarkNetNode must be called before Shutdown().

If the test doesn't wait long enough before sending the quit signal, then the
order in which the functions are called changes. This then leads to some tests
failing. Therefore, tests become dependent on the performance of the computer
they are run on.

Also, in quitTest() the time.Sleep() should have been called in a separate
go-routine. This lead to the exit channel containing the interrupt signal before
NewCmd() is called. Leading to a race condition between Run() and Shutdown().

Increasing the quitting time and sleeping in a separate go-routine should fix
the problem. We also don't want to unnecessarily increase the test time, since
we want to have quick feedback.
